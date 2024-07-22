# FreshNews
RPA to extract data and images from a News Website

## 1. Deploy Using Virtual Environment in Windows

Install the Virtual Environment

```sh
pip install virtualenv
```

Activate the virtual environment

```sh
venv\Scripts\activate
```

Install the dependencies

```sh
pip install -r requirements.txt
```

Run the app.py

```sh
python -m tasks.main
```

## 2. Deploy Using Robocorp

Configure the WorkItems

Input:
    #Example
    {
        "search_phrase": "climate change",
        "topic": "California",
        "number_of_months": 1
    }

## Output

- **Files:** [`scraped_news.xlsx`, `*.(jpg,png)`]
- **Location:** `output` folder

