import assert from 'node:assert/strict'
// eslint-disable-next-line test/no-import-node-test -- Run with Bun without adding a test framework.
import { describe, it } from 'node:test'
import { createEvent, proxyRequest } from 'h3'
import { createSsrCookieForwarder } from '../app/utils/ssr-cookies'
import { createOAuthProxyFetch } from '../server/utils/oauth-proxy'

const tokens = { access_token: 'new-access', refresh_token: 'new-refresh', expires_in: 900, token_type: 'Bearer' }

describe('OAuth proxy', () => {
    it('sends only the final response through h3, after saving the session cookie', async () => {
        const headers = new Map<string, string | number | string[]>()
        const chunks: Uint8Array[] = []
        let ended = false
        let calls = 0
        const event = createEvent(
            { headers: {}, method: 'GET' } as Parameters<typeof createEvent>[0],
            {
                statusCode: 200,
                getHeader: (name: string) => headers.get(name),
                setHeader(name: string, value: string | number | string[]) {
                    assert.equal(ended, false)
                    headers.set(name, value)
                },
                write(chunk: Uint8Array) { chunks.push(chunk) },
                end() { ended = true },
                get writableEnded() { return ended },
            } as unknown as Parameters<typeof createEvent>[1],
        )
        await proxyRequest(event, 'https://backend.test', {
            fetch: createOAuthProxyFetch({
                fetch: async () => {
                    calls++
                    return Response.json({ code: calls === 1 ? 401 : 200 }, { status: calls === 1 ? 401 : 200 })
                },
                refresh: async () => tokens,
                save: async () => {
                    assert.equal(ended, false)
                    assert.equal(chunks.length, 0)
                    event.node.res.setHeader('set-cookie', 'nuxt-session=new; HttpOnly')
                },
                clear: async () => { assert.fail('must not log out') },
            }),
        })
        assert.equal(event.node.res.statusCode, 200)
        assert.equal(ended, true)
        assert.equal(headers.get('set-cookie'), 'nuxt-session=new; HttpOnly')
        assert.equal(new TextDecoder().decode(Buffer.concat(chunks)), '{"code":200}')
    })

    it('saves the session before retrying and replays POST bodies', async () => {
        const steps: string[] = []
        const body = new TextEncoder().encode('{"name":"test"}')
        let calls = 0
        const fetch = createOAuthProxyFetch({
            fetch: async (_input, init) => {
                assert.equal(init?.body, body)
                assert.equal(init?.method, 'POST')
                if (++calls === 1)
                    return Response.json({ code: 401 }, { status: 401 })
                assert.equal(new Headers(init?.headers).get('authorization'), 'Bearer new-access')
                steps.push('retry')
                return Response.json({ code: 200 })
            },
            refresh: async () => {
                steps.push('refresh')
                return tokens
            },
            save: async () => { steps.push('save') },
            clear: async () => { assert.fail('must not log out') },
        })
        assert.equal((await fetch('https://backend.test', { method: 'POST', body })).status, 200)
        assert.deepEqual(steps, ['refresh', 'save', 'retry'])
    })

    it('does not refresh other upstream status codes', async () => {
        for (const status of [200, 403, 503]) {
            const response = new Response('original', { status })
            const fetch = createOAuthProxyFetch({
                fetch: async () => response,
                refresh: async () => { assert.fail('must not refresh') },
                save: async () => { assert.fail('must not save') },
                clear: async () => { assert.fail('must not log out') },
            })
            assert.equal(await fetch('https://backend.test'), response)
        }
    })

    it('clears the session only for an invalid refresh token', async () => {
        let cleared = false
        const fetch = createOAuthProxyFetch({
            fetch: async () => new Response('', { status: 401 }),
            refresh: async () => { throw Object.assign(new Error('invalid'), { statusCode: 400, data: { error: 'invalid_grant' } }) },
            save: async () => { assert.fail('must not save') },
            clear: async () => { cleared = true },
        })
        assert.equal((await fetch('https://backend.test')).status, 401)
        assert.equal(cleared, true)
    })

    it('keeps the session on network, server and client-configuration errors', async () => {
        for (const error of [new Error('timeout'), { statusCode: 500 }, { statusCode: 401, data: { error: 'invalid_client' } }]) {
            const fetch = createOAuthProxyFetch({
                fetch: async () => new Response('', { status: 401 }),
                refresh: async () => { throw error },
                save: async () => { assert.fail('must not save') },
                clear: async () => { assert.fail('must not log out') },
            })
            const response = await fetch('https://backend.test')
            assert.equal(response.status, 503)
            assert.equal((await response.json()).code, 503)
        }
    })

    it('keeps the new session if retrying the business request fails', async () => {
        let calls = 0
        let saved = false
        const fetch = createOAuthProxyFetch({
            fetch: async () => {
                if (++calls === 1)
                    return new Response('', { status: 401 })
                throw new Error('business API disconnected')
            },
            refresh: async () => tokens,
            save: async () => { saved = true },
            clear: async () => { assert.fail('must not log out') },
        })
        await assert.rejects(fetch('https://backend.test'), /business API disconnected/)
        assert.equal(saved, true)
        assert.equal(calls, 2)
    })

    it('does not loop when the retry is also unauthorized', async () => {
        let calls = 0
        const fetch = createOAuthProxyFetch({
            fetch: async () => {
                calls++
                return new Response('', { status: 401 })
            },
            refresh: async () => tokens,
            save: async () => {},
            clear: async () => { assert.fail('refresh succeeded') },
        })
        assert.equal((await fetch('https://backend.test')).status, 401)
        assert.equal(calls, 2)
    })
})

describe('SSR session cookies', () => {
    it('forwards rotated cookies to the browser and subsequent SSR API requests', () => {
        const headers = new Map<string, string | string[]>()
        const event = createEvent(
            { headers: { cookie: 'nuxt-session=old; preference=dark' } } as Parameters<typeof createEvent>[0],
            {
                getHeader: (name: string) => headers.get(name),
                setHeader: (name: string, value: string | string[]) => headers.set(name, value),
            } as unknown as Parameters<typeof createEvent>[1],
        )
        const cookies = createSsrCookieForwarder(event)
        const response = new Headers()
        response.append('set-cookie', 'nuxt-session=new=value; Path=/; HttpOnly')
        response.append('set-cookie', 'nuxt-session.1=chunk; Path=/; HttpOnly')
        cookies.onResponse(response)
        assert.equal(cookies.requestCookie(), 'nuxt-session=new=value; preference=dark; nuxt-session.1=chunk')
        assert.deepEqual(headers.get('set-cookie'), response.getSetCookie())
        cookies.onResponse(new Headers({ 'set-cookie': 'nuxt-session.1=; Max-Age=0; Path=/' }))
        assert.equal(cookies.requestCookie(), 'nuxt-session=new=value; preference=dark')
    })
})
