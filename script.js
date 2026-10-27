
importScripts("https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.sw.js");


let allPrices = [];
let chart = null;
let currentFilteredPrices = [];


/* -----------------------------
   LOAD DATA
----------------------------- */

async function loadPrices() {

  try {

    const response = await fetch("prices.json?" + Date.now());

    if (!response.ok) {
      throw new Error("Could not load prices.json");
    }

    allPrices = await response.json();

    if (!Array.isArray(allPrices) || allPrices.length === 0) {
      throw new Error("prices.json does not contain price history.");
    }

    updateCurrentPrice();

    drawChart("today");

  } catch (error) {

    console.error(error);

    const errorBox = document.getElementById("error");

    errorBox.textContent = error.message;
    errorBox.style.display = "block";

  }

}


/* -----------------------------
   CURRENT PRICE
----------------------------- */

function updateCurrentPrice() {

  const latest = allPrices[allPrices.length - 1];

  document.getElementById("regularPrice").textContent =
    `$${Number(latest.regular).toFixed(3)}`;

  document.getElementById("premiumPrice").textContent =
    `$${Number(latest.premium).toFixed(3)}`;

  const date = new Date(latest.checked_at);

  const formattedDate = date.toLocaleString("en-CA", {
    dateStyle: "medium",
    timeStyle: "short"
  });

  document.getElementById("regularUpdated").textContent =
    `Updated ${formattedDate}`;

  document.getElementById("premiumUpdated").textContent =
    `Updated ${formattedDate}`;

}


/* -----------------------------
   DRAW CHART
----------------------------- */

function drawChart(range) {

  const now = new Date();
  let cutoff;

  if (range === "today") {
    // Start of today in the visitor's local timezone.
    cutoff = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  } else {
    cutoff = Date.now() - Number(range) * 24 * 60 * 60 * 1000;
  }

  currentFilteredPrices = allPrices.filter(price => {
    return new Date(price.checked_at).getTime() >= cutoff;
  });

  const days = range === "today" ? 1 : Number(range);

  const labels = currentFilteredPrices.map(price => {
    return new Date(price.checked_at);
  });

  const regular = currentFilteredPrices.map(price =>
    Number(price.regular)
  );

  const premium = currentFilteredPrices.map(price =>
    Number(price.premium)
  );

  const ctx = document.getElementById("priceChart");

  if (chart) {
    chart.destroy();
  }

  /*
   * For 7D, calculate a tighter Y-axis range.
   */
  let yScaleOptions = {};

  if (days === 7 && currentFilteredPrices.length > 0) {

    const allValues = [
      ...regular,
      ...premium
    ];

    const minPrice = Math.min(...allValues);
    const maxPrice = Math.max(...allValues);

    // Add a small amount of padding around the actual prices
    const padding = 0.005;

    const yMin =
      Math.floor((minPrice - padding) * 1000) / 1000;

    const yMax =
      Math.ceil((maxPrice + padding) * 1000) / 1000;

    yScaleOptions = {

      min: yMin,
      max: yMax,

      ticks: {

        stepSize: 0.005,

        callback: function(value) {

          return "$" + Number(value).toFixed(3);

        }

      }

    };

  } else {

    // Normal automatic scale for 30D, 3M and 1Y

    yScaleOptions = {

      ticks: {

        callback: function(value) {

          return "$" + Number(value).toFixed(3);

        }

      }

    };

  }

  chart = new Chart(ctx, {

    type: "line",

    data: {

      labels: labels,

      datasets: [

        {
          label: "Regular",

          data: regular,

          borderColor: "#2563eb",

          backgroundColor: "rgba(37,99,235,0.08)",

          borderWidth: 2,

          pointRadius: 4,

          pointHoverRadius: 8,

          pointHitRadius: 12,

          tension: 0.25
        },

        {
          label: "Premium",

          data: premium,

          borderColor: "#dc2626",

          backgroundColor: "rgba(220,38,38,0.08)",

          borderWidth: 2,

          pointRadius: 4,

          pointHoverRadius: 8,

          pointHitRadius: 12,

          tension: 0.25
        }

      ]

    },

    options: {

      responsive: true,

      maintainAspectRatio: false,

      interaction: {

        mode: "index",

        intersect: false

      },

      onClick: function(event, elements) {

        if (!elements.length) {
          return;
        }

        const index = elements[0].index;

        const selectedRecord =
          currentFilteredPrices[index];

        if (selectedRecord) {

          showSelectedDate(selectedRecord);

        }

      },

      plugins: {

        legend: {

          display: true

        },

        tooltip: {

          enabled: true,

          mode: "index",

          intersect: false,

          callbacks: {

            title: function(context) {

              const date =
                new Date(context[0].parsed.x);

              return date.toLocaleString("en-CA", {

                dateStyle: "medium",

                timeStyle: "short"

              });

            },

            label: function(context) {

              return (
                `${context.dataset.label}: ` +
                `$${Number(context.parsed.y).toFixed(3)}/L`
              );

            }

          }

        }

      },

      scales: {

        x: {

          type: "time",

          time: {

            unit: "day",

            tooltipFormat: "MMM d, h:mm a",

            displayFormats: {

              day: "MMM d"

            }

          }

        },

        y: yScaleOptions

      }

    }

  });

}

/* -----------------------------
   SHOW SELECTED DATE
----------------------------- */

function showSelectedDate(selectedRecord) {

  /*
    Convert selected timestamp into
    a calendar date.

    This lets us find every price check
    that happened on that same day.
  */

  const selectedDate =
    new Date(selectedRecord.checked_at);

  const year = selectedDate.getFullYear();

  const month = selectedDate.getMonth();

  const day = selectedDate.getDate();


  const sameDay = allPrices.filter(price => {

    const date = new Date(price.checked_at);

    return (

      date.getFullYear() === year &&

      date.getMonth() === month &&

      date.getDate() === day

    );

  });


  const formattedDate =
    selectedDate.toLocaleDateString("en-CA", {

      year: "numeric",

      month: "long",

      day: "numeric"

    });


  document.getElementById("selectedDateTitle").textContent =
    formattedDate;


  const body =
    document.getElementById("selectedDateBody");

  body.innerHTML = "";


  sameDay.forEach(price => {

    const date =
      new Date(price.checked_at);


    const time =
      date.toLocaleTimeString("en-CA", {

        hour: "numeric",

        minute: "2-digit"

      });


    const row =
      document.createElement("tr");


    row.innerHTML = `

      <td>${time}</td>

      <td class="regular-value">
        $${Number(price.regular).toFixed(3)}
      </td>

      <td class="premium-value">
        $${Number(price.premium).toFixed(3)}
      </td>

    `;


    body.appendChild(row);

  });


  document.getElementById("selectedDate").style.display =
    "block";

}


/* -----------------------------
   RANGE BUTTONS
----------------------------- */

document.querySelectorAll(".range-buttons button")
  .forEach(button => {

    button.addEventListener("click", () => {

      document.querySelectorAll(".range-buttons button")
        .forEach(btn =>
          btn.classList.remove("active")
        );

      button.classList.add("active");

      /*
        Hide previously selected date
        when changing the graph range.
      */

      document.getElementById("selectedDate").style.display =
        "none";

      drawChart(button.dataset.range || Number(button.dataset.days));

    });

  });


/* -----------------------------
   START
----------------------------- */

loadPrices();
