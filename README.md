# 🌍 Toward Global Large Language Models in Medicine

<p align="center">
 <img src="https://img.shields.io/badge/Languages-20-green" />
 <img src="https://img.shields.io/badge/Entries-500K%2B-brightgreen" />
 <img src="https://img.shields.io/badge/LLMs_Evaluated-56-blue" />
</p>

## 📢 News
- **[2025.01]** 🔥 GlobMed is publicly available through the Hugging Face platform.  

## GlobMed
We introduce GlobMed, the largest multilingual medical dataset to date, spanning 20 languages.

### Scale & Coverage
- **800,000+ entries**
- **20 languages**
  - High-resource: Arabic, Chinese, English, French, German, Hindi, Indonesian, Japanese, Korean, Portuguese, Russian, Spanish, Thai
  - Low-resource: Bengali, Malay, Swahili, Urdu, Wolof, Yoruba, Zulu
 
<p align="center">
  <img src="fig/map.svg"/>
</p>

### Core Tasks
- **Natural Language Inference:** BioNLI, MedNLI
- **Long-Form Question Answering:** ExpertQA-Bio, ExpertQA-Med, LiveQA 
- **Multiple-choice Question Answering:** HeadQA, MedExpQA, MedQA, MMLU-Pro  

## GlobMed-Bench

Building on GlobMed, we establish GlobMed-Bench, which systematically assesses 56 state-of-the-art LLMs across multiple multilingual medical tasks.

### Evaluation Scope
- **56 state-of-the-art LLMs**
- **40,000+ independent experiments**
- **125M+ generated responses**

- Overall Performance of 12 Proprietary LLMs
    <p align="center">
      <img src="fig/bench1.svg"/>
    </p>
- Overall Performance of 44 Open-Weight LLMs
    <p align="center">
      <img src="fig/bench2.svg"/>
    </p>
    

### Key Findings
- Proprietary LLMs achieve higher average performance but within a narrow range  
- Open-weight LLMs show large variance and strong scaling effects  
- Significant performance disparities across languages, especially on low-resource languages
- Reasoning-enhanced LLMs consistently outperform non-reasoning counterparts  
- 

## GlobMed-LLMs
## Usage

### Load Dataset
GlobMed datasets are hosted on the Hugging Face platform and can be loaded using the `datasets` library.

```python
from datasets import load_dataset

# Load GlobMed-MMLU-Pro dataset (English)
globmed_mmlu_pro = load_dataset("ruiyang-medinfo/GlobMed_MMLU-Pro", "en")

# Access train and test splits
globmed_mmlu_pro_train = globmed_mmlu_pro["train"]
globmed_mmlu_pro_test = globmed_mmlu_pro["test"]
```
## Contact
- **Rui Yang**: yang.rui@duke-nus.edu.sg
- **Weihao Xuan**: xuan@ms.k.u-tokyo.ac.jp
- **Dr. Nan Liu**: liu.nan@duke-nus.edu.sg

## Citation
```

```

## License
This repository is licensed under the [MIT](https://github.com/microsoft/PEACE/blob/main/LICENSE) license.
