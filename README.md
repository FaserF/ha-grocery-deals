<div align="center">
  <img src="custom_components/grocery_deals/brand/logo.png" alt="Grocery Deals Banner" width="400">
  <h1>Grocery Deals (for Home Assistant) 🛒🏷️</h1>
  <p><strong>Universal Supermarket Deals & Discount Aggregator for Home Assistant. Automatically aggregates offers across REWE, EDEKA, Lidl, ALDI, and Norma to find the best prices and notify you when your favorite products are on sale!</strong></p>

  [![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://hacs.xyz)
  [![Downloads](https://img.shields.io/github/downloads/FaserF/ha-grocery-deals/latest/grocery_deals.zip?label=Downloads&style=for-the-badge)](https://github.com/FaserF/ha-grocery-deals/releases)
  [![GitHub Release](https://img.shields.io/github/v/release/FaserF/ha-grocery-deals?style=for-the-badge)](https://github.com/FaserF/ha-grocery-deals/releases)
  [![License](https://img.shields.io/github/license/FaserF/ha-grocery-deals?style=for-the-badge)](LICENSE)
</div>

---

## 🧭 Quick Links

| | | | |
| :--- | :--- | :--- | :--- |
| [✨ Features](#-features) | [🛒 Supported Supermarkets](#-supported-supermarkets) | [📦 Installation](#-installation) | [⚙️ Configuration](#-configuration) |
| [🛠️ Options Flow](#-options-flow) | [❤️ Sponsors](#-support-this-project) | [📄 License](#-license) | |

---

## 🛒 Supported Supermarkets

> [!IMPORTANT]
> **Requirement**: You must have **at least two** of the following supermarket integrations installed and configured in Home Assistant so Grocery Deals can compare prices and find the cheapest store:

| Supermarket | Integration & Repository | Features Provided |
| :--- | :--- | :--- |
| 🔴 **REWE** | [**ha-rewe**](https://github.com/FaserF/ha-rewe) | Weekly offers, REWE Bonus coupons, recalls |
| 🟡 **EDEKA** | [**ha-edeka**](https://github.com/FaserF/ha-edeka) | Regional market offers & discounts |
| 🔵 **Lidl** | [**ha-lidl**](https://github.com/FaserF/ha-lidl) | Weekly offers, Lidl Plus coupons, digital receipts |
| ⚪ **ALDI** | [**ha-aldi**](https://github.com/FaserF/ha-aldi) | ALDI Süd / ALDI Nord weekly flyers & deals |
| 🔴 **Norma** | [**ha-norma**](https://github.com/FaserF/ha-norma) | Weekly store discounts & promotional brochures |

---

## ✨ Features

- **🔍 Custom Keyword Filtering**:
  - Configure any list of search terms (e.g. `Monster Energy`, `Butter`, `Kaffee`, `Gurke`).
  - For each keyword, a dedicated sensor is generated:
    - **State**: Current best price & store (e.g., `0,88 € (Lidl)`) or `Nicht im Angebot`.
    - **Attributes**:
      - `on_sale`: `True` / `False`
      - `best_price`: Lowest price found across all markets
      - `best_store`: Name of the market offering the best price
      - `on_sale_stores`: List of all markets where the item is currently on sale
      - `all_prices`: Complete price breakdown grouped by supermarket
      - `offers`: All matching offer details with images, validity dates, base prices, and pack sizes.
- **🚀 Dynamic Auto-Discovery**:
  - Automatically discovers when 2 or more supermarket integrations are set up on your Home Assistant.
  - Zero-touch prompt to enable the aggregator hub.
- **📊 Hub Overview Sensor**:
  - Shows the total count of active deals across all your keywords and lists which stores are connected.
- **⚡ Zero Additional API Load**:
  - Seamlessly re-uses the cached coordinator data from your installed supermarket integrations without spamming external supermarket APIs.

---

## ❤️ Support This Project

> I maintain this integration in my **free time alongside my regular job**.
>
> **This project is and will always remain 100% free.**
>
> Donations are completely voluntary — but they help me stay motivated and dedicate more time to maintaining open-source tools!

<div align="center">

[![PayPal](https://img.shields.io/badge/Donate%20via-PayPal-%2300457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/FaserF)

</div>

---

## 📦 Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Click on the three dots in the top right corner and select **Custom repositories**.
3. Add `FaserF/ha-grocery-deals` with category **Integration**.
4. Search for **Grocery Deals**.
5. Click **Download** and restart Home Assistant.

### Manual Installation

1. Download `grocery_deals.zip` from the latest release.
2. Extract into `<config>/custom_components/grocery_deals/`.
3. Restart Home Assistant.

---

## ⚙️ Configuration & Options

1. Go to **Settings > Devices & Services > Add Integration**.
2. Search for **Grocery Deals**.
3. The setup screen will show you which supermarket integrations were detected and which ones you can optionally install from GitHub.
4. Enter your desired search filter keywords.
5. Done! You can modify or add new filter keywords anytime via the **Configure** (Options) button.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
