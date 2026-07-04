# Gas Company Scraper

A simple Python tool to find and scrape info from natural gas company websites (focus on Russia, but you can change that).

---

## What it does

- Searches Google (via SerpAPI) for company URLs  
- Crawls each website (respects robots.txt, limited depth)  
- Extracts: emails, phones, address, products, production capacity  
- Saves everything to an Excel file  

---

## Quick start

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   pip install lxml   # needed for fast HTML parsing
   ```

2. **Get a SerpAPI key** from [serpapi.com](https://serpapi.com/) and put it in a `.env` file:  
   ```
   SERPAPI_KEY=your_key_here
   ```

3. **Adjust config.py** if you want (countries, keywords, max companies).

4. **Run it**  
   ```bash
   python main.py
   ```

5. **Find the result** in `output/companies.xlsx`.

---

## Customize

- Change `COUNTRIES` in `config.py` (e.g., `["USA", "Canada"]`).  
- Change `SEARCH_KEYWORDS` – they come from `keywords.py`.  
- Tweak quality score threshold in `validator.py` (default: 20).

---

## License

MIT – do whatever you want, just don't blame me if it breaks!!!
