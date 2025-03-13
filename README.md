
# 📚 Unofficial Inventaire.io API (Python)

This project was born out of the need to create a Python-based API to automate interactions with [Inventaire.io](https://inventaire.io).  
Although Inventaire does provide a native API, it’s not very intuitive or well-documented — hence, this project was created to offer a more accessible alternative via browser automation.

⚠️ **Important:** This is an unofficial, scraping-based API using Selenium. Use responsibly.

---

## ✨ Features

- ✅ Login to Inventaire.io  
- ✅ Search by ISBN  
- ✅ Create new Work (Book)  
- 🔜 Create Edition from a Work *(in progress)*  
- 🔜 Add Edition to your Inventory *(planned)*  
- 🔜 Manage your Inventory *(planned)*  
- 🔜 Handle transactions *(planned)*

---

## 📦 Dependencies

### Python Dependencies (install via `pip`)
```bash
pip install selenium unidecode
```

> ✅ Tested with:
- `selenium>=4.29.0`  
- `Unidecode>=1.3.8`

### System Dependencies
Make sure you have **Google Chrome** installed on your system:
- `google-chrome >= 132.0`

Also, ensure that **ChromeDriver** (matching your Chrome version) is accessible in your system `PATH`.

---

## 🚀 Getting Started

### Basic Example:

```python
from inventaire_api import InventaireApi

api = InventaireApi()

if api.login("your_username", "your_password"):
    api.create_work("The Little Prince", "Antoine de Saint-Exupéry")
    result = api.search_by_isbn("9780156012195")
    print(f"Book found at: {result}")
else:
    print("Login failed")

api.close()
```

---

## 🛣️ Roadmap

- [x] Login to Inventaire.io  
- [x] Search by ISBN  
- [x] Create new Work (Book)  
- [ ] Create Edition from Work  
- [ ] Add Edition to Inventory  
- [ ] Manage Inventory (update/delete)  
- [ ] Manage Transactions

---

## ⚠️ Disclaimer

This is an **unofficial API** based on **web scraping** with Selenium.  
Since it depends on the structure of the Inventaire.io frontend (which can change at any time), this tool might become unstable or break without notice.

> The use of automated tools may go against Inventaire.io’s terms of use. Use at your own risk — and consider contacting the Inventaire staff if you're building a serious tool or integration.

---

## 🤝 Contributions

Pull requests are welcome! Feel free to improve, expand, or refactor this tool.

---
