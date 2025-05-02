# Anuvaad Bulk Translate

Bulk translation utility supporting scanned and computer-generated documents for the Anuvaad platform.

## 1. Pre-requisites

Ensure the following folder structure exists before starting the script:

- `input/`
- `output/`
- `digitization/`

### Notes:
- For digitized (computer-generated) documents: name your files with `_digitized.pdf` suffix (e.g., `filename_digitized.pdf`).
- For scanned documents: any filename is acceptable.

## 2. Translate Only (Pre-digitized/Computer-Generated Documents)

Run the script:

```bash
python3 translate_only_new.py
```

## 3. Digitization + Translation (Scanned Documents)

Run the script:

```bash
python3 app.py
```

## 4. General Configuration

To switch between environments, modify the URLs in `config/config.py`:

* **Users instance**:
  `users-auth.tarento.com`
* **SUVAS JUD instance**:
  `jud-auth.anuvaad.org`

Update your user credentials in:

```python
config/credentials.py
```

## 5. Dependencies

Ensure the following are installed and configured locally:

* Python 3
* `pymongo`
* MongoDB

Update the MongoDB server host URL in `config.py` accordingly.

## 6. Language Change

To change the language:

1. Log into the Anuvaad UI and run a sample job for the desired language.
2. Update the `modelID` and `language code` in:

```python
service/api_calls.py  # Inside the translate() function
```

> The `modelID` is critical for successful translation (e.g., `en-pa` is `126`).

Alternatively, refer to similar language implementations in other files inside the `service/` folder (e.g., Hindi, Tamil, etc.).

## 7. Output Handling

* Translated documents will be generated in `.docx` format.
* Compress the translated `.docx` files into a `.zip` archive.
* Upload the `.zip` to the designated S3 bucket:

```
s3://anuvaad-raw-datasets/
```

---

© [Aswin Pradeep](https://github.com/aswinpradeep) | [GitHub Repo](https://github.com/aswinpradeep/anuvaad-bulk-translate)

---

Acknowledgment: Rathan Muralidhar for contributing the script.

---

**Note:** This README file is edited and committed using MCP.