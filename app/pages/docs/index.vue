<script setup lang="ts">
function handleImageError(event: Event) {
    const target = event.target as HTMLImageElement
    target.style.display = 'none'
}
</script>

<template>
    <div class="docs-home">
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-background" />
            <div class="hero-content">
                <div class="hero-text">
                    <h1 class="hero-title">
                        <span class="title-text">UsagiPass</span>
                    </h1>
                    <p class="hero-subtitle">
                        动态生成可登录的 DXPASS
                    </p>
                    <p class="hero-description">
                        从零开始美化你的玩家二维码
                    </p>
                    <div class="hero-actions">
                        <NuxtLink to="/begin" class="btn btn-primary">
                            <Icon name="heroicons:rocket-launch" class="btn-icon" />
                            开始使用
                        </NuxtLink>
                        <NuxtLink to="/implementation" class="btn btn-secondary">
                            <Icon name="heroicons:book-open" class="btn-icon" />
                            查看手册
                        </NuxtLink>
                        <a href="https://github.com/TrueRou/UsagiPass" target="_blank" class="btn btn-tertiary">
                            <Icon name="heroicons:star" class="btn-icon" />
                            Star on GitHub
                        </a>
                    </div>
                </div>

                <!-- Decorative Character -->
                <div class="hero-decoration">
                    <img
                        src="https://maimai.sega.jp/storage/root/chara.png"
                        alt="Character"
                        class="decoration-char"
                        @error="handleImageError"
                    >
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="features-section">
            <div class="container">
                <div class="features-grid">
                    <!-- Feature 1: 动态生成 -->
                    <div class="feature-card">
                        <div class="feature-icon">
                            <Icon name="heroicons:sparkles" />
                        </div>
                        <h3 class="feature-title">
                            动态生成
                        </h3>
                        <p class="feature-description">
                            基于水鱼 / 落雪查分器的数据动态生成玩家的 DXPASS，用户个性化数据云端储存。
                        </p>
                    </div>

                    <!-- Feature 2: 高度自定义 -->
                    <div class="feature-card">
                        <div class="feature-icon">
                            <Icon name="heroicons:paint-brush" />
                        </div>
                        <h3 class="feature-title">
                            高度自定义
                        </h3>
                        <p class="feature-description">
                            自定义 DXPASS 背景、外框、角色，支持使用预设素材或个性化上传自己的图片。
                        </p>
                    </div>

                    <!-- Feature 3: 支持登录 -->
                    <div class="feature-card">
                        <div class="feature-icon">
                            <Icon name="heroicons:qr-code" />
                        </div>
                        <h3 class="feature-title">
                            支持登录
                        </h3>
                        <p class="feature-description">
                            通过代理直接嵌入微信玩家二维码页面，可直接扫描 DXPASS 上机，逼格满满。
                        </p>
                    </div>

                    <!-- Feature 4: 更新查分器 -->
                    <div class="feature-card">
                        <div class="feature-icon">
                            <Icon name="heroicons:arrow-path" />
                        </div>
                        <h3 class="feature-title">
                            更新查分器
                        </h3>
                        <p class="feature-description">
                            支持一键更新水鱼 / 落雪查分器，无需复杂的配置。
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Community Section -->
        <section class="community-section">
            <div class="container">
                <div class="community-card">
                    <Icon name="heroicons:user-group" class="community-icon" />
                    <h3 class="community-title">
                        加入我们的社区
                    </h3>
                    <p class="community-text">
                        欢迎加入 UsagiPass 兔兔群：<span class="highlight">363346002</span>
                    </p>
                    <div class="community-links">
                        <a href="https://turou.fun/" target="_blank" class="link-item">
                            <Icon name="heroicons:globe-alt" />
                            博客
                        </a>
                        <a href="https://afdian.com/a/turou" target="_blank" class="link-item">
                            <Icon name="heroicons:heart" />
                            赞助支持
                        </a>
                    </div>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="footer">
            <div class="container">
                <p class="footer-text">
                    Copyright  2019-2025 TuRou
                </p>
            </div>
        </footer>
    </div>
</template>

<style scoped>
.docs-home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
}

/* Hero Section */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #6366f1 100%);
  animation: gradientShift 15s ease infinite;
}

@keyframes gradientShift {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 1200px;
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.hero-text {
  color: white;
  animation: fadeInUp 1s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-title {
  font-size: 4rem;
  font-weight: 900;
  margin: 0 0 1rem 0;
  line-height: 1.1;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.title-text {
  display: inline-block;
  background: linear-gradient(45deg, #ffffff, #fde68a, #ffffff);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.hero-subtitle {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  opacity: 0.95;
}

.hero-description {
  font-size: 1.25rem;
  margin: 0 0 2rem 0;
  opacity: 0.85;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.75rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 1rem;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.btn-primary {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #1f2937;
}

.btn-primary:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 25px rgba(251, 191, 36, 0.5);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px) scale(1.05);
}

.btn-tertiary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.btn-tertiary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px) scale(1.05);
}

.hero-decoration {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.decoration-char {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.3));
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

/* Features Section */
.features-section {
  position: relative;
  padding: 6rem 2rem;
  background: linear-gradient(180deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem;
  border-radius: 1.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: fadeInScale 0.6s ease-out backwards;
}

.feature-card:nth-child(1) { animation-delay: 0.1s; }
.feature-card:nth-child(2) { animation-delay: 0.2s; }
.feature-card:nth-child(3) { animation-delay: 0.3s; }
.feature-card:nth-child(4) { animation-delay: 0.4s; }

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.feature-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(139, 92, 246, 0.3);
}

.feature-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  color: white;
  font-size: 2rem;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.feature-description {
  font-size: 1rem;
  line-height: 1.6;
  color: #6b7280;
  margin: 0;
}

/* Community Section */
.community-section {
  padding: 4rem 2rem;
  background: white;
}

.community-card {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  padding: 3rem;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.community-icon {
  width: 4rem;
  height: 4rem;
  color: #d97706;
  margin: 0 auto 1.5rem;
}

.community-title {
  font-size: 2rem;
  font-weight: 700;
  color: #78350f;
  margin: 0 0 1rem 0;
}

.community-text {
  font-size: 1.25rem;
  color: #92400e;
  margin: 0 0 2rem 0;
}

.highlight {
  font-weight: 700;
  color: #b45309;
  background: rgba(255, 255, 255, 0.5);
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
}

.community-links {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.link-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: white;
  color: #92400e;
  text-decoration: none;
  border-radius: 9999px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.link-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(217, 119, 6, 0.3);
  background: #fef3c7;
}

/* Footer */
.footer {
  padding: 2rem;
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  color: white;
  text-align: center;
}

.footer-text {
  margin: 0;
  opacity: 0.7;
  font-size: 0.875rem;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.25rem;
  }

  .hero-description {
    font-size: 1rem;
  }

  .hero-decoration {
    display: none;
  }

  .hero-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .features-section {
    padding: 3rem 1rem;
  }

  .community-card {
    padding: 2rem 1.5rem;
  }

  .community-links {
    flex-direction: column;
  }

  .link-item {
    width: 100%;
    justify-content: center;
  }

  .float-circle {
    display: none;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 1rem;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1.125rem;
  }

  .community-title {
    font-size: 1.5rem;
  }

  .community-text {
    font-size: 1rem;
  }
}
</style>
