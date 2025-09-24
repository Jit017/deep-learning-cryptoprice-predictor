// Next-Level Enhanced JavaScript for FutureCoin
document.addEventListener("DOMContentLoaded", () => {
  initializeApp()
})

function initializeApp() {
  // Initialize all components
  initializeNavigation()
  initializeAnimations()
  initializeScrollEffects()
  initializeParticles()

  // Page-specific initializations
  if (document.getElementById("crypto-select")) {
    initializePredictionsPage()
  }
  if (document.getElementById("comparison-crypto")) {
    initializeComparisonPage()
  }

  // Initialize advanced features
  initializeAdvancedFeatures()
}

// Enhanced Navigation with Advanced Effects
function initializeNavigation() {
  const hamburger = document.querySelector(".hamburger")
  const navMenu = document.querySelector(".nav-menu")
  const navbar = document.querySelector(".navbar")

  if (hamburger && navMenu) {
    hamburger.addEventListener("click", () => {
      hamburger.classList.toggle("active")
      navMenu.classList.toggle("active")

      // Add body scroll lock when menu is open
      document.body.style.overflow = hamburger.classList.contains("active") ? "hidden" : ""
    })

    // Close menu when clicking on a link
    document.querySelectorAll(".nav-link").forEach((link) =>
      link.addEventListener("click", () => {
        hamburger.classList.remove("active")
        navMenu.classList.remove("active")
        document.body.style.overflow = ""
      }),
    )
  }

  // Advanced navbar scroll effects
  let lastScrollY = window.scrollY
  window.addEventListener("scroll", () => {
    const currentScrollY = window.scrollY

    if (navbar) {
      if (currentScrollY > 100) {
        navbar.style.background = "rgba(10, 10, 15, 0.95)"
        navbar.style.backdropFilter = "blur(25px) saturate(200%)"
        navbar.style.borderBottom = "1px solid rgba(255, 255, 255, 0.15)"
      } else {
        navbar.style.background = "rgba(10, 10, 15, 0.8)"
        navbar.style.backdropFilter = "blur(20px) saturate(180%)"
        navbar.style.borderBottom = "1px solid rgba(255, 255, 255, 0.1)"
      }

      // Hide/show navbar on scroll
      if (currentScrollY > lastScrollY && currentScrollY > 200) {
        navbar.style.transform = "translateY(-100%)"
      } else {
        navbar.style.transform = "translateY(0)"
      }
    }

    lastScrollY = currentScrollY
  })
}

// Advanced Animation System
function initializeAnimations() {
  // Intersection Observer for scroll animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible")

        // Add stagger effect for grid items
        if (entry.target.classList.contains("stagger-children")) {
          const children = entry.target.children
          Array.from(children).forEach((child, index) => {
            setTimeout(() => {
              child.classList.add("visible")
            }, index * 100)
          })
        }
      }
    })
  }, observerOptions)

  // Observe elements for animation
  const animateElements = document.querySelectorAll(
    ".feature-card, .coin-card, .result-card, .metric-item, .insight-card",
  )

  animateElements.forEach((el, index) => {
    el.classList.add("fade-in-up")
    el.style.animationDelay = `${index * 0.1}s`
    observer.observe(el)
  })

  // Add stagger animation to grids
  document.querySelectorAll(".features-grid, .coins-grid, .results-grid").forEach((grid) => {
    grid.classList.add("stagger-children")
    observer.observe(grid)
  })
}

// Advanced Scroll Effects
function initializeScrollEffects() {
  // Parallax effect for hero section
  const hero = document.querySelector(".hero")
  if (hero) {
    window.addEventListener("scroll", () => {
      const scrolled = window.pageYOffset
      const rate = scrolled * -0.5
      hero.style.transform = `translateY(${rate}px)`
    })
  }

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })
}

// Advanced Particle System
function initializeParticles() {
  const canvas = document.createElement("canvas")
  const ctx = canvas.getContext("2d")

  canvas.style.position = "fixed"
  canvas.style.top = "0"
  canvas.style.left = "0"
  canvas.style.width = "100%"
  canvas.style.height = "100%"
  canvas.style.pointerEvents = "none"
  canvas.style.zIndex = "-1"
  canvas.style.opacity = "0.3"

  document.body.appendChild(canvas)

  function resizeCanvas() {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }

  resizeCanvas()
  window.addEventListener("resize", resizeCanvas)

  const particles = []
  const particleCount = 50

  class Particle {
    constructor() {
      this.x = Math.random() * canvas.width
      this.y = Math.random() * canvas.height
      this.vx = (Math.random() - 0.5) * 0.5
      this.vy = (Math.random() - 0.5) * 0.5
      this.size = Math.random() * 2 + 1
      this.opacity = Math.random() * 0.5 + 0.2
    }

    update() {
      this.x += this.vx
      this.y += this.vy

      if (this.x < 0 || this.x > canvas.width) this.vx *= -1
      if (this.y < 0 || this.y > canvas.height) this.vy *= -1
    }

    draw() {
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(0, 245, 255, ${this.opacity})`
      ctx.fill()
    }
  }

  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle())
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    particles.forEach((particle) => {
      particle.update()
      particle.draw()
    })

    // Draw connections
    particles.forEach((particle, i) => {
      particles.slice(i + 1).forEach((otherParticle) => {
        const dx = particle.x - otherParticle.x
        const dy = particle.y - otherParticle.y
        const distance = Math.sqrt(dx * dx + dy * dy)

        if (distance < 100) {
          ctx.beginPath()
          ctx.moveTo(particle.x, particle.y)
          ctx.lineTo(otherParticle.x, otherParticle.y)
          ctx.strokeStyle = `rgba(0, 245, 255, ${0.1 * (1 - distance / 100)})`
          ctx.lineWidth = 1
          ctx.stroke()
        }
      })
    })

    requestAnimationFrame(animate)
  }

  animate()
}

// Enhanced Cryptocurrency Data
const cryptoData = {
  BTC: {
    name: "Bitcoin",
    symbol: "BTC",
    currentPrice: 43250.75,
    change24h: 2.34,
    hourlyModel: { mae: 125.5, rmse: 189.25, r2: 0.892, accuracy: 89.2 },
    dailyModel: { mae: 1250.75, rmse: 1890.5, r2: 0.756, accuracy: 75.6 },
    color: "#f7931a",
    gradient: "linear-gradient(135deg, #f7931a 0%, #ff6b35 100%)",
  },
  ETH: {
    name: "Ethereum",
    symbol: "ETH",
    currentPrice: 2650.25,
    change24h: -1.45,
    hourlyModel: { mae: 45.25, rmse: 67.8, r2: 0.885, accuracy: 88.5 },
    dailyModel: { mae: 125.5, rmse: 189.75, r2: 0.742, accuracy: 74.2 },
    color: "#627eea",
    gradient: "linear-gradient(135deg, #627eea 0%, #00d4ff 100%)",
  },
  ADA: {
    name: "Cardano",
    symbol: "ADA",
    currentPrice: 0.485,
    change24h: 3.67,
    hourlyModel: { mae: 0.012, rmse: 0.018, r2: 0.876, accuracy: 87.6 },
    dailyModel: { mae: 0.035, rmse: 0.052, r2: 0.721, accuracy: 72.1 },
    color: "#0033ad",
    gradient: "linear-gradient(135deg, #0033ad 0%, #7c3aed 100%)",
  },
  BNB: {
    name: "Binance Coin",
    symbol: "BNB",
    currentPrice: 315.8,
    change24h: 1.89,
    hourlyModel: { mae: 8.25, rmse: 12.5, r2: 0.881, accuracy: 88.1 },
    dailyModel: { mae: 22.75, rmse: 34.25, r2: 0.738, accuracy: 73.8 },
    color: "#f3ba2f",
    gradient: "linear-gradient(135deg, #f3ba2f 0%, #ff6b35 100%)",
  },
  DOGE: {
    name: "Dogecoin",
    symbol: "DOGE",
    currentPrice: 0.0825,
    change24h: 5.23,
    hourlyModel: { mae: 0.0025, rmse: 0.0038, r2: 0.863, accuracy: 86.3 },
    dailyModel: { mae: 0.0075, rmse: 0.0112, r2: 0.695, accuracy: 69.5 },
    color: "#c2a633",
    gradient: "linear-gradient(135deg, #c2a633 0%, #f59e0b 100%)",
  },
  SOL: {
    name: "Solana",
    symbol: "SOL",
    currentPrice: 98.45,
    change24h: -2.15,
    hourlyModel: { mae: 2.85, rmse: 4.25, r2: 0.889, accuracy: 88.9 },
    dailyModel: { mae: 8.5, rmse: 12.75, r2: 0.751, accuracy: 75.1 },
    color: "#9945ff",
    gradient: "linear-gradient(135deg, #9945ff 0%, #7c3aed 100%)",
  },
  MATIC: {
    name: "Polygon",
    symbol: "MATIC",
    currentPrice: 0.875,
    change24h: 0.95,
    hourlyModel: { mae: 0.025, rmse: 0.038, r2: 0.872, accuracy: 87.2 },
    dailyModel: { mae: 0.065, rmse: 0.095, r2: 0.718, accuracy: 71.8 },
    color: "#8247e5",
    gradient: "linear-gradient(135deg, #8247e5 0%, #00d4ff 100%)",
  },
}

// Chart instances
let predictionChart

// Enhanced Predictions Page
function initializePredictionsPage() {
  console.log("Initializing next-level predictions page...")

  const elements = {
    cryptoSelect: document.getElementById("crypto-select"),
    daysAheadInput: document.getElementById("days-ahead"),
    hoursAheadInput: document.getElementById("hours-ahead"),
    currentPriceInput: document.getElementById("current-price"),
    predictBtn: document.getElementById("predict-btn"),
  }

  // Set initial values with enhanced animations
  updateCurrentPrice()

  // Enhanced event listeners
  if (elements.cryptoSelect) {
    elements.cryptoSelect.addEventListener("change", () => {
      updateCurrentPrice()
      addRippleEffect(elements.cryptoSelect)
    })
  }

  if (elements.daysAheadInput) {
    elements.daysAheadInput.addEventListener("input", () => {
      validateInputs()
      addInputGlow(elements.daysAheadInput)
    })
  }

  if (elements.hoursAheadInput) {
    elements.hoursAheadInput.addEventListener("input", () => {
      validateInputs()
      addInputGlow(elements.hoursAheadInput)
    })
  }

  if (elements.predictBtn) {
    elements.predictBtn.addEventListener("click", generatePrediction)
    addButtonEffects(elements.predictBtn)
  }

  // Initialize advanced chart
  initializePredictionChart()
}

// Enhanced UI Effects
function addRippleEffect(element) {
  const ripple = document.createElement("span")
  ripple.classList.add("ripple")
  ripple.style.position = "absolute"
  ripple.style.borderRadius = "50%"
  ripple.style.background = "rgba(0, 245, 255, 0.3)"
  ripple.style.transform = "scale(0)"
  ripple.style.animation = "ripple 0.6s linear"
  ripple.style.left = "50%"
  ripple.style.top = "50%"

  element.style.position = "relative"
  element.style.overflow = "hidden"
  element.appendChild(ripple)

  setTimeout(() => {
    ripple.remove()
  }, 600)
}

function addInputGlow(element) {
  element.style.boxShadow = "0 0 20px rgba(0, 245, 255, 0.3)"
  setTimeout(() => {
    element.style.boxShadow = ""
  }, 300)
}

function addButtonEffects(button) {
  button.addEventListener("mouseenter", () => {
    button.style.transform = "translateY(-2px) scale(1.02)"
    button.style.boxShadow = "0 10px 30px rgba(0, 245, 255, 0.4)"
  })

  button.addEventListener("mouseleave", () => {
    button.style.transform = ""
    button.style.boxShadow = ""
  })
}

// Enhanced Price Update with Animations
function updateCurrentPrice() {
  const selectedCrypto = document.getElementById("crypto-select")?.value
  const data = cryptoData[selectedCrypto]

  if (!data) return

  const elements = {
    currentSymbol: document.getElementById("current-symbol"),
    currentPriceDisplay: document.getElementById("current-price-display"),
    currentPriceInput: document.getElementById("current-price"),
    changeElement: document.querySelector(".change-value"),
    dailySymbol: document.getElementById("daily-prediction-symbol"),
    hourlySymbol: document.getElementById("hourly-prediction-symbol"),
  }

  // Animate price updates
  if (elements.currentPriceDisplay) {
    elements.currentPriceDisplay.style.transform = "scale(1.1)"
    elements.currentPriceDisplay.style.color = data.color
    setTimeout(() => {
      elements.currentPriceDisplay.style.transform = ""
      elements.currentPriceDisplay.style.color = ""
    }, 300)
  }

  // Update values with enhanced formatting
  if (elements.currentSymbol) elements.currentSymbol.textContent = data.symbol
  if (elements.currentPriceDisplay) {
    elements.currentPriceDisplay.textContent = `$${data.currentPrice.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 8,
    })}`
  }
  if (elements.currentPriceInput) elements.currentPriceInput.value = data.currentPrice

  if (elements.changeElement) {
    const changeValue = data.change24h
    elements.changeElement.textContent = `${changeValue > 0 ? "+" : ""}${changeValue.toFixed(2)}%`
    elements.changeElement.className = `change-value ${changeValue > 0 ? "positive" : "negative"}`

    // Add pulse animation for significant changes
    if (Math.abs(changeValue) > 5) {
      elements.changeElement.style.animation = "pulse 1s ease-in-out"
      setTimeout(() => {
        elements.changeElement.style.animation = ""
      }, 1000)
    }
  }

  // Update prediction symbols
  if (elements.dailySymbol) elements.dailySymbol.textContent = data.symbol
  if (elements.hourlySymbol) elements.hourlySymbol.textContent = data.symbol
}

// Enhanced Input Validation
function validateInputs() {
  const daysAhead = Number.parseInt(document.getElementById("days-ahead")?.value) || 0
  const hoursAhead = Number.parseInt(document.getElementById("hours-ahead")?.value) || 0
  const predictBtn = document.getElementById("predict-btn")

  if (!predictBtn) return

  if (daysAhead === 0 && hoursAhead === 0) {
    predictBtn.disabled = true
    predictBtn.textContent = "Select days or hours ahead"
    predictBtn.style.opacity = "0.5"
  } else {
    predictBtn.disabled = false
    predictBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Prediction'
    predictBtn.style.opacity = "1"
  }
}

// Enhanced Prediction Generation
async function generatePrediction() {
  console.log("Generating next-level prediction...")

  const elements = {
    cryptoSelect: document.getElementById("crypto-select"),
    daysAheadInput: document.getElementById("days-ahead"),
    hoursAheadInput: document.getElementById("hours-ahead"),
    currentPriceInput: document.getElementById("current-price"),
    predictBtn: document.getElementById("predict-btn"),
  }

  const selectedCrypto = elements.cryptoSelect?.value
  const daysAhead = Number.parseInt(elements.daysAheadInput?.value) || 0
  const hoursAhead = Number.parseInt(elements.hoursAheadInput?.value) || 0
  const currentPrice = elements.currentPriceInput?.value ? Number.parseFloat(elements.currentPriceInput.value) : null

  // Enhanced validation
  if (daysAhead === 0 && hoursAhead === 0) {
    showNotification("Please select at least one prediction timeframe", "warning")
    return
  }

  if (currentPrice && currentPrice <= 0) {
    showNotification("Please enter a valid current price", "error")
    return
  }

  // Enhanced loading state
  if (elements.predictBtn) {
    const originalText = elements.predictBtn.innerHTML
    elements.predictBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Magic...'
    elements.predictBtn.disabled = true
    elements.predictBtn.style.background = "linear-gradient(135deg, #ff3366 0%, #7c3aed 100%)"

    try {
      // Simulate enhanced API call with better error handling
      await simulateAdvancedPrediction(selectedCrypto, daysAhead, hoursAhead, currentPrice)

      showNotification("Predictions generated successfully!", "success")
    } catch (error) {
      console.error("Enhanced prediction error:", error)
      showNotification(`Prediction failed: ${error.message}`, "error")
    } finally {
      // Restore button state with animation
      elements.predictBtn.innerHTML = originalText
      elements.predictBtn.disabled = false
      elements.predictBtn.style.background = ""
    }
  }
}

// Enhanced Notification System
function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `notification notification-${type}`
  notification.style.cssText = `
    position: fixed;
    top: 100px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    color: white;
    font-weight: 600;
    z-index: 10000;
    transform: translateX(400px);
    transition: all 0.3s ease;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
  `

  const colors = {
    success: "linear-gradient(135deg, #10b981 0%, #00ff88 100%)",
    error: "linear-gradient(135deg, #ef4444 0%, #ff3366 100%)",
    warning: "linear-gradient(135deg, #f59e0b 0%, #ff6b35 100%)",
    info: "linear-gradient(135deg, #00f5ff 0%, #7c3aed 100%)",
  }

  notification.style.background = colors[type] || colors.info
  notification.textContent = message

  document.body.appendChild(notification)

  // Animate in
  setTimeout(() => {
    notification.style.transform = "translateX(0)"
  }, 100)

  // Animate out
  setTimeout(() => {
    notification.style.transform = "translateX(400px)"
    setTimeout(() => {
      notification.remove()
    }, 300)
  }, 4000)
}

// Enhanced Simulation Function
async function simulateAdvancedPrediction(crypto, days, hours, price) {
  // Simulate network delay with progress
  await new Promise((resolve) => setTimeout(resolve, 800))

  const data = cryptoData[crypto]
  if (!data) throw new Error("Cryptocurrency not found")

  const basePrice = price || data.currentPrice

  // Generate more realistic predictions
  const predictions = {}

  if (days > 0) {
    const volatility = Math.random() * 0.1 + 0.05 // 5-15% volatility
    const trend = (Math.random() - 0.5) * 0.2 // -10% to +10% trend
    const predictedPrice = basePrice * (1 + trend + (Math.random() - 0.5) * volatility)

    predictions.daily_prediction = {
      predicted_price: Math.max(0, predictedPrice),
      days_ahead: days,
      confidence: Math.random() * 0.3 + 0.7, // 70-100% confidence
      model_accuracy: data.dailyModel.accuracy,
    }
  }

  if (hours > 0) {
    const volatility = Math.random() * 0.05 + 0.01 // 1-6% volatility
    const trend = (Math.random() - 0.5) * 0.1 // -5% to +5% trend
    const predictedPrice = basePrice * (1 + trend + (Math.random() - 0.5) * volatility)

    predictions.hourly_prediction = {
      predicted_price: Math.max(0, predictedPrice),
      hours_ahead: hours,
      confidence: Math.random() * 0.2 + 0.8, // 80-100% confidence
      model_accuracy: data.hourlyModel.accuracy,
    }
  }

  predictions.symbol = crypto
  predictions.current_price = basePrice

  // Update UI with enhanced animations
  updatePredictionResults(predictions)

  return predictions
}

// Enhanced Results Update
function updatePredictionResults(data) {
  // Update daily prediction with animations
  if (data.daily_prediction) {
    const dailyCard = document.getElementById("daily-prediction-card")
    const dailyPrice = document.getElementById("daily-prediction-price")
    const dailySymbol = document.getElementById("daily-prediction-symbol")
    const dailyDays = document.getElementById("daily-days-ahead")

    if (dailyCard && dailyPrice && dailySymbol && dailyDays) {
      dailyCard.style.display = "block"
      dailyCard.style.animation = "slideInUp 0.5s ease-out"

      // Animate price update
      dailyPrice.style.transform = "scale(0)"
      setTimeout(() => {
        dailyPrice.textContent = `$${data.daily_prediction.predicted_price.toLocaleString("en-US", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 8,
        })}`
        dailyPrice.style.transform = "scale(1)"
        dailyPrice.style.transition = "transform 0.3s ease"
      }, 200)

      dailySymbol.textContent = data.symbol
      dailyDays.textContent = data.daily_prediction.days_ahead
    }
  }

  // Update hourly prediction with animations
  if (data.hourly_prediction) {
    const hourlyCard = document.getElementById("hourly-prediction-card")
    const hourlyPrice = document.getElementById("hourly-prediction-price")
    const hourlySymbol = document.getElementById("hourly-prediction-symbol")
    const hourlyHours = document.getElementById("hourly-hours-ahead")

    if (hourlyCard && hourlyPrice && hourlySymbol && hourlyHours) {
      hourlyCard.style.display = "block"
      hourlyCard.style.animation = "slideInUp 0.5s ease-out 0.2s both"

      // Animate price update
      hourlyPrice.style.transform = "scale(0)"
      setTimeout(() => {
        hourlyPrice.textContent = `$${data.hourly_prediction.predicted_price.toLocaleString("en-US", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 8,
        })}`
        hourlyPrice.style.transform = "scale(1)"
        hourlyPrice.style.transition = "transform 0.3s ease"
      }, 400)

      hourlySymbol.textContent = data.symbol
      hourlyHours.textContent = data.hourly_prediction.hours_ahead
    }
  }

  // Update forecast range with enhanced calculations
  updateForecastRange(data)

  // Update chart
  if (predictionChart) {
    const labels = []
    const actual = []
    const predicted = []

    // Build a short synthetic series around current price
    const base = data.current_price || 0
    for (let i = 0; i < 12; i++) {
      labels.push(`${i}`)
      const noise = (Math.random() - 0.5) * 0.02
      actual.push(base * (1 + noise))
    }

    // Plot predicted point(s)
    let predPointIndex = 11
    let predValue = base
    if (data.daily_prediction) {
      predValue = data.daily_prediction.predicted_price
    } else if (data.hourly_prediction) {
      predValue = data.hourly_prediction.predicted_price
    }
    predicted.length = actual.length
    for (let i = 0; i < predicted.length; i++) predicted[i] = null
    predicted[predPointIndex] = predValue

    predictionChart.data.labels = labels
    predictionChart.data.datasets[0].data = actual
    predictionChart.data.datasets[1].data = predicted
    predictionChart.update()
  }
}

// Enhanced Forecast Range Update
function updateForecastRange(data) {
  const forecastLow = document.getElementById("forecast-low")
  const forecastHigh = document.getElementById("forecast-high")

  if (!forecastLow || !forecastHigh) return

  let minPrice = Number.POSITIVE_INFINITY
  let maxPrice = Number.NEGATIVE_INFINITY

  if (data.daily_prediction) {
    const price = data.daily_prediction.predicted_price
    const volatility = 0.15 // 15% volatility range
    minPrice = Math.min(minPrice, price * (1 - volatility))
    maxPrice = Math.max(maxPrice, price * (1 + volatility))
  }

  if (data.hourly_prediction) {
    const price = data.hourly_prediction.predicted_price
    const volatility = 0.08 // 8% volatility range
    minPrice = Math.min(minPrice, price * (1 - volatility))
    maxPrice = Math.max(maxPrice, price * (1 + volatility))
  }

  if (minPrice !== Number.POSITIVE_INFINITY && maxPrice !== Number.NEGATIVE_INFINITY) {
    // Animate the forecast range update
    forecastLow.style.opacity = "0"
    forecastHigh.style.opacity = "0"

    setTimeout(() => {
      forecastLow.textContent = `$${minPrice.toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 8,
      })}`
      forecastHigh.textContent = `$${maxPrice.toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 8,
      })}`

      forecastLow.style.opacity = "1"
      forecastHigh.style.opacity = "1"
      forecastLow.style.transition = "opacity 0.3s ease"
      forecastHigh.style.transition = "opacity 0.3s ease"
    }, 300)
  }
}

// Advanced Features Initialization
function initializeAdvancedFeatures() {
  // Add keyboard shortcuts
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case "p":
          e.preventDefault()
          const predictBtn = document.getElementById("predict-btn")
          if (predictBtn && !predictBtn.disabled) {
            predictBtn.click()
          }
          break
        case "r":
          e.preventDefault()
          location.reload()
          break
      }
    }
  })

  // Add theme toggle (if needed)
  initializeThemeToggle()

  // Add performance monitoring
  initializePerformanceMonitoring()
}

// Theme Toggle (for future dark/light mode)
function initializeThemeToggle() {
  // Placeholder for theme toggle functionality
  console.log("Theme system initialized")
}

// Performance Monitoring
function initializePerformanceMonitoring() {
  // Monitor page load performance
  window.addEventListener("load", () => {
    const loadTime = performance.now()
    console.log(`Page loaded in ${loadTime.toFixed(2)}ms`)

    // Log to analytics if needed
    if (loadTime > 3000) {
      console.warn("Page load time is slow:", loadTime)
    }
  })
}

// Charts
function initializePredictionChart() {
  const ctx = document.getElementById("prediction-chart")?.getContext("2d")
  if (!ctx || typeof Chart === "undefined") return

  predictionChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Actual Price",
          data: [],
          borderColor: "#60a5fa",
          backgroundColor: "rgba(96,165,250,0.15)",
          tension: 0.3,
          pointRadius: 0,
        },
        {
          label: "AI Prediction",
          data: [],
          borderColor: "#34d399",
          backgroundColor: "rgba(52,211,153,0.15)",
          tension: 0.0,
          pointRadius: 4,
          showLine: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: "rgba(255,255,255,0.05)" } },
        y: { grid: { color: "rgba(255,255,255,0.05)" } },
      },
      plugins: {
        legend: { labels: { color: "#e5e7eb" } },
        tooltip: { mode: "index", intersect: false },
      },
    },
  })
}

function initializeComparisonPage() {
  // Comparison bar chart
  const cmpCtx = document.getElementById("comparison-chart")?.getContext("2d")
  if (cmpCtx && typeof Chart !== "undefined") {
    const labels = Object.keys(cryptoData)
    const hourly = labels.map((k) => cryptoData[k].hourlyModel.accuracy)
    const daily = labels.map((k) => cryptoData[k].dailyModel.accuracy)

    new Chart(cmpCtx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          { label: "Hourly Accuracy %", data: hourly, backgroundColor: "rgba(52,211,153,0.6)" },
          { label: "Daily Accuracy %", data: daily, backgroundColor: "rgba(96,165,250,0.6)" },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true, max: 100 } },
        plugins: { legend: { labels: { color: "#e5e7eb" } } },
      },
    })
  }

  // Accuracy distribution radar chart
  const accCtx = document.getElementById("accuracy-distribution-chart")?.getContext("2d")
  if (accCtx && typeof Chart !== "undefined") {
    const labels = Object.keys(cryptoData)
    const accuracies = labels.map((k) => cryptoData[k].hourlyModel.accuracy)

    new Chart(accCtx, {
      type: "radar",
      data: {
        labels,
        datasets: [
          {
            label: "Hourly Accuracy %",
            data: accuracies,
            backgroundColor: "rgba(0,245,255,0.2)",
            borderColor: "rgba(0,245,255,0.8)",
            pointBackgroundColor: "#00f5ff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { r: { angleLines: { color: "rgba(255,255,255,0.1)" }, grid: { color: "rgba(255,255,255,0.1)" }, suggestedMin: 0, suggestedMax: 100 } },
        plugins: { legend: { labels: { color: "#e5e7eb" } } },
      },
    })
  }
}

// Add CSS animations
const style = document.createElement("style")
style.textContent = `
  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
  }
  
  @keyframes ripple {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
`
document.head.appendChild(style)
