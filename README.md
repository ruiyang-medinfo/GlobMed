# 🌍 Toward Global Large Language Models in Medicine

<p align="center">
 <img src="https://img.shields.io/badge/Languages-20-green" />
 <img src="https://img.shields.io/badge/Entries-500K%2B-brightgreen" />
 <img src="https://img.shields.io/badge/LLMs_Evaluated-56-blue" />
</p>

<p align="center">
  <a href="https://arxiv.org/abs/XXXX.XXXXX"><b>[📜 Paper]</b></a> •
  <a href="https://huggingface.co/collections/GlobMed"><b>[🤗 HuggingFace]</b></a>
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

### Core Tasks
- **Natural Language Inference (NLI)**
- **Long-Form Question Answering (QA)**
- **Multiple-choice Question Answering (MCQA)**

### Data Sources
- **NLI:** BioNLI, MedNLI  
- **Long-Form QA:** ExpertQA-Bio, ExpertQA-Med, LiveQA  
- **MCQA:** HeadQA, MedExpQA, MedQA, MMLU-Pro  

## GlobMed-Bench

Building on GlobMed, we establish GlobMed-Bench, which systematically assesses 56 state-of-the-art LLMs across multiple multilingual medical tasks.

### Evaluation Scope
- **56 state-of-the-art LLMs**
  - 12 proprietary LLMs
  - 44 open-weight LLMs
- **40,000+ independent experiments**
- **125M+ generated responses**

### Key Findings
- Proprietary LLMs achieve higher average performance but within a narrow range  
- Open-weight LLMs show large variance and strong scaling effects  
- Significant performance disparities across languages, especially on low-resource languages
- Reasoning-enhanced LLMs consistently outperform non-reasoning counterparts  


## 5. GlobMed-LLMs

To reduce cross-lingual disparities, we fine-tuned several LLMs on GlobMed.

### Models
- MedGemma-4B
- Qwen3 series (1.7B / 4B / 8B)

## 7. Usage

### Load Dataset

## 8. Contact
For any inquiries or concerns, feel free to reach out to us via Email: [Rui Yang](yang.rui@duke-nus.edu.sg) and [xxxxx](xxxxxxxxx).

## 9. Citation
```

```

## 10. License
This repository is licensed under the [MIT](https://github.com/microsoft/PEACE/blob/main/LICENSE) License.
