// Mobile Navigation Toggle
document.addEventListener("DOMContentLoaded", () => {
  const hamburger = document.querySelector(".hamburger")
  const navMenu = document.querySelector(".nav-menu")

  if (hamburger && navMenu) {
    hamburger.addEventListener("click", () => {
      hamburger.classList.toggle("active")
      navMenu.classList.toggle("active")
    })

    // Close menu when clicking on a link
    document.querySelectorAll(".nav-link").forEach((n) =>
      n.addEventListener("click", () => {
        hamburger.classList.remove("active")
        navMenu.classList.remove("active")
      }),
    )
  }
})

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

// Add scroll effect to navbar
window.addEventListener("scroll", () => {
  const navbar = document.querySelector(".navbar")
  if (window.scrollY > 50) {
    navbar.style.background = "rgba(10, 10, 10, 0.98)"
  } else {
    navbar.style.background = "rgba(10, 10, 10, 0.95)"
  }
})

// Intersection Observer for animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "1"
      entry.target.style.transform = "translateY(0)"
    }
  })
}, observerOptions)

// Observe elements for animation
document.addEventListener("DOMContentLoaded", () => {
  const animateElements = document.querySelectorAll(".feature-card, .coin-card")
  animateElements.forEach((el) => {
    el.style.opacity = "0"
    el.style.transform = "translateY(20px)"
    el.style.transition = "opacity 0.6s ease, transform 0.6s ease"
    observer.observe(el)
  })
})

// Cryptocurrency data and prediction logic
const cryptoData = {
  BTC: {
    name: "Bitcoin",
    symbol: "BTC",
    currentPrice: 43250.75,
    change24h: 2.34,
    hourlyModel: { mae: 125.5, rmse: 189.25, r2: 0.892, accuracy: 89.2 },
    dailyModel: { mae: 1250.75, rmse: 1890.5, r2: 0.756, accuracy: 75.6 },
  },
  ETH: {
    name: "Ethereum",
    symbol: "ETH",
    currentPrice: 2650.25,
    change24h: -1.45,
    hourlyModel: { mae: 45.25, rmse: 67.8, r2: 0.885, accuracy: 88.5 },
    dailyModel: { mae: 125.5, rmse: 189.75, r2: 0.742, accuracy: 74.2 },
  },
  ADA: {
    name: "Cardano",
    symbol: "ADA",
    currentPrice: 0.485,
    change24h: 3.67,
    hourlyModel: { mae: 0.012, rmse: 0.018, r2: 0.876, accuracy: 87.6 },
    dailyModel: { mae: 0.035, rmse: 0.052, r2: 0.721, accuracy: 72.1 },
  },
  BNB: {
    name: "Binance Coin",
    symbol: "BNB",
    currentPrice: 315.8,
    change24h: 1.89,
    hourlyModel: { mae: 8.25, rmse: 12.5, r2: 0.881, accuracy: 88.1 },
    dailyModel: { mae: 22.75, rmse: 34.25, r2: 0.738, accuracy: 73.8 },
  },
  DOGE: {
    name: "Dogecoin",
    symbol: "DOGE",
    currentPrice: 0.0825,
    change24h: 5.23,
    hourlyModel: { mae: 0.0025, rmse: 0.0038, r2: 0.863, accuracy: 86.3 },
    dailyModel: { mae: 0.0075, rmse: 0.0112, r2: 0.695, accuracy: 69.5 },
  },
  SOL: {
    name: "Solana",
    symbol: "SOL",
    currentPrice: 98.45,
    change24h: -2.15,
    hourlyModel: { mae: 2.85, rmse: 4.25, r2: 0.889, accuracy: 88.9 },
    dailyModel: { mae: 8.5, rmse: 12.75, r2: 0.751, accuracy: 75.1 },
  },
  MATIC: {
    name: "Polygon",
    symbol: "MATIC",
    currentPrice: 0.875,
    change24h: 0.95,
    hourlyModel: { mae: 0.025, rmse: 0.038, r2: 0.872, accuracy: 87.2 },
    dailyModel: { mae: 0.065, rmse: 0.095, r2: 0.718, accuracy: 71.8 },
  },
}

let predictionChart = null
let comparisonChart = null
let accuracyDistributionChart = null

// Initialize predictions page
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("crypto-select")) {
    initializePredictionsPage()
  }
  if (document.getElementById("comparison-crypto")) {
    initializeComparisonPage()
  }
})

function initializePredictionsPage() {
  console.log('Initializing predictions page...')
  const cryptoSelect = document.getElementById("crypto-select")
  const daysAheadInput = document.getElementById("days-ahead")
  const hoursAheadInput = document.getElementById("hours-ahead")
  const currentPriceInput = document.getElementById("current-price")
  const predictBtn = document.getElementById("predict-btn")

  console.log('Elements found:', {
    cryptoSelect: !!cryptoSelect,
    daysAheadInput: !!daysAheadInput,
    hoursAheadInput: !!hoursAheadInput,
    currentPriceInput: !!currentPriceInput,
    predictBtn: !!predictBtn
  })

  // Set initial values
  updateCurrentPrice()

  // Event listeners
  if (cryptoSelect) cryptoSelect.addEventListener("change", updateCurrentPrice)
  if (daysAheadInput) daysAheadInput.addEventListener("input", validateInputs)
  if (hoursAheadInput) hoursAheadInput.addEventListener("input", validateInputs)
  if (predictBtn) {
    predictBtn.addEventListener("click", generatePrediction)
    console.log('Button click listener added')
  } else {
    console.error('Predict button not found!')
  }

  // Initialize chart
  initializePredictionChart()
}

function updateCurrentPrice() {
  const selectedCrypto = document.getElementById("crypto-select").value
  const data = cryptoData[selectedCrypto]

  if (!data) {
    console.warn('No data available for', selectedCrypto)
    return
  }

  const currentSymbol = document.getElementById("current-symbol")
  const currentPriceDisplay = document.getElementById("current-price-display")
  const currentPriceInput = document.getElementById("current-price")
  const changeElement = document.querySelector(".change-value")

  if (currentSymbol) currentSymbol.textContent = data.symbol
  if (currentPriceDisplay) currentPriceDisplay.textContent = `$${data.currentPrice.toLocaleString()}`
  if (currentPriceInput) currentPriceInput.value = data.currentPrice

  if (changeElement) {
    const changeValue = data.change24h
    changeElement.textContent = `${changeValue > 0 ? "+" : ""}${changeValue.toFixed(2)}%`
    changeElement.className = `change-value ${changeValue > 0 ? "positive" : "negative"}`
  }

  // Update prediction symbols
  const dailySymbol = document.getElementById("daily-prediction-symbol")
  const hourlySymbol = document.getElementById("hourly-prediction-symbol")
  if (dailySymbol) dailySymbol.textContent = data.symbol
  if (hourlySymbol) hourlySymbol.textContent = data.symbol
}

function validateInputs() {
  const daysAhead = parseInt(document.getElementById("days-ahead").value) || 0
  const hoursAhead = parseInt(document.getElementById("hours-ahead").value) || 0
  
  // Ensure at least one prediction type is selected
  if (daysAhead === 0 && hoursAhead === 0) {
    document.getElementById("predict-btn").disabled = true
    document.getElementById("predict-btn").textContent = "Select days or hours ahead"
  } else {
    document.getElementById("predict-btn").disabled = false
    document.getElementById("predict-btn").innerHTML = '<i class="fas fa-magic"></i> Generate Prediction'
  }
}

async function generatePrediction() {
  console.log('Generate prediction clicked!')
  try {
    const selectedCrypto = document.getElementById("crypto-select").value
    const daysAhead = parseInt(document.getElementById("days-ahead").value) || 0
    const hoursAhead = parseInt(document.getElementById("hours-ahead").value) || 0
    const currentPrice = document.getElementById("current-price").value ? 
      Number.parseFloat(document.getElementById("current-price").value) : null

    console.log('Input values:', { selectedCrypto, daysAhead, hoursAhead, currentPrice })

    // Validate inputs
    if (daysAhead === 0 && hoursAhead === 0) {
      alert("Please select at least one prediction timeframe (days or hours ahead)")
      return
    }

    if (currentPrice && currentPrice <= 0) {
      alert("Please enter a valid current price")
      return
    }

    // Show loading state
    const predictBtn = document.getElementById("predict-btn")
    const originalText = predictBtn.innerHTML
    predictBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...'
    predictBtn.disabled = true

    try {
      // Call enhanced prediction API
      const modelName = selectedCrypto.toLowerCase()
      const requestBody = {
        symbol: selectedCrypto,
        days_ahead: daysAhead,
        hours_ahead: hoursAhead
      }
      
      if (currentPrice) {
        requestBody.current_price = currentPrice
      }

      const resp = await fetch(`/api/predict/${modelName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
      }

      const data = await resp.json()
      console.log('API Response:', data)
      
      // Update current price if provided
      if (data.current_price) {
        const currentPriceDisplay = document.getElementById("current-price-display")
        if (currentPriceDisplay) {
          currentPriceDisplay.textContent = `$${data.current_price.toLocaleString()}`
        }
      }

      // Update daily prediction
      if (data.daily_prediction) {
        const dailyCard = document.getElementById("daily-prediction-card")
        const dailyPrice = document.getElementById("daily-prediction-price")
        const dailySymbol = document.getElementById("daily-prediction-symbol")
        const dailyDays = document.getElementById("daily-days-ahead")
        
        if (dailyCard && dailyPrice && dailySymbol && dailyDays) {
          dailyCard.style.display = "block"
          dailyPrice.textContent = `₹${data.daily_prediction.predicted_price.toLocaleString()}`
          dailySymbol.textContent = data.symbol
          dailyDays.textContent = data.daily_prediction.days_ahead
          console.log('Daily prediction updated:', data.daily_prediction)
        } else {
          console.error('Daily prediction elements not found')
        }
      } else {
        const dailyCard = document.getElementById("daily-prediction-card")
        if (dailyCard) {
          dailyCard.style.display = "none"
        }
      }

      // Update hourly prediction
      if (data.hourly_prediction) {
        const hourlyCard = document.getElementById("hourly-prediction-card")
        const hourlyPrice = document.getElementById("hourly-prediction-price")
        const hourlySymbol = document.getElementById("hourly-prediction-symbol")
        const hourlyHours = document.getElementById("hourly-hours-ahead")
        
        if (hourlyCard && hourlyPrice && hourlySymbol && hourlyHours) {
          hourlyCard.style.display = "block"
          hourlyPrice.textContent = `$${data.hourly_prediction.predicted_price.toLocaleString()}`
          hourlySymbol.textContent = data.symbol
          hourlyHours.textContent = data.hourly_prediction.hours_ahead
          console.log('Hourly prediction updated:', data.hourly_prediction)
        } else {
          console.error('Hourly prediction elements not found')
        }
      } else {
        const hourlyCard = document.getElementById("hourly-prediction-card")
        if (hourlyCard) {
          hourlyCard.style.display = "none"
        }
      }

      // Update forecast range based on predictions
      updateForecastRange(data)

      // Show success message
      console.log('Predictions generated successfully!')
      alert('Predictions generated successfully! Check the prediction cards below.')

    } catch (error) {
      console.error('API Error:', error)
      alert(`Prediction failed: ${error.message}`)
    } finally {
      // Restore button state
      predictBtn.innerHTML = originalText
      predictBtn.disabled = false
    }

  } catch (err) {
    console.error('Prediction error:', err)
    alert('Prediction failed. Please try again.')
  }
}

function updateForecastRange(data) {
  const forecastLow = document.getElementById("forecast-low")
  const forecastHigh = document.getElementById("forecast-high")
  
  let minPrice = Infinity
  let maxPrice = -Infinity
  
  if (data.daily_prediction) {
    const price = data.daily_prediction.predicted_price
    minPrice = Math.min(minPrice, price * 0.98)
    maxPrice = Math.max(maxPrice, price * 1.02)
  }
  
  if (data.hourly_prediction) {
    const price = data.hourly_prediction.predicted_price
    minPrice = Math.min(minPrice, price * 0.98)
    maxPrice = Math.max(maxPrice, price * 1.02)
  }
  
  if (minPrice !== Infinity && maxPrice !== -Infinity) {
    forecastLow.textContent = `$${minPrice.toLocaleString()}`
    forecastHigh.textContent = `$${maxPrice.toLocaleString()}`
  }
}

// Placeholder chart functions if referenced elsewhere
function initializePredictionChart() {}
function initializeComparisonPage() {}
