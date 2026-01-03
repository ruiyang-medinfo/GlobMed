# 🌍 Toward Global Large Language Models in Medicine

<p align="center">
 <img src="https://img.shields.io/badge/Languages-20-green" />
 <img src="https://img.shields.io/badge/Entries-500K%2B-brightgreen" />
 <img src="https://img.shields.io/badge/LLMs_Evaluated-56-blue" />
</p>

<p align="center">
  <a href="https://arxiv.org/abs/XXXX.XXXXX"><b>[📜 Paper]</b></a> •
  <a href="https://huggingface.co/collections/GlobMed"><b>[🤗 HuggingFace]</b></a> •
  <a href="https://github.com/GlobMed/GlobMed"><b>[🐱 GitHub]</b></a>
</p>


## 📢 News
- **[2025.01]** 🔥 GlobMed repository released  
- **[2025.02]** 🔥 500K+ multilingual medical entries across 12 languages  
- **[2025.03]** 🔥 GlobMed-Bench released, evaluating 56 LLMs  


## 1. Motivation

Recent large language models (LLMs) have demonstrated strong medical reasoning abilities. 
However, progress in this area is constrained by the lack of **large-scale, high-quality multilingual medical datasets**.

Most existing medical datasets:
- focus on a single language, predominantly English,
- cover only a limited subset of medical tasks,
- or lack the scale and consistency required for systematic multilingual evaluation.

Without a unified multilingual medical dataset, it is difficult to:
- reliably evaluate LLM performance across languages,
- quantify cross-lingual performance disparities,
- or benchmark models in realistic global medical settings.

**GlobMed is introduced as a large-scale multilingual medical dataset**, covering 12 languages and three core medical tasks (NLI, long-form QA, and MCQA).  
Crucially, GlobMed is **designed with benchmarking in mind**, enabling consistent and systematic evaluation across languages, tasks, and model families.

Building on GlobMed, we further establish **GlobMed-Bench**, which leverages this dataset to provide the most comprehensive multilingual medical benchmark to date.



## 2. What is GlobMed?

GlobMed is a **comprehensive benchmark suite** consisting of:

- **GlobMed**: a large-scale multilingual medical dataset  
- **GlobMed-Bench**: a systematic evaluation benchmark  
- **GlobMed-LLMs**: multilingual medical LLMs fine-tuned on GlobMed  

Together, these resources support **global, equitable development of medical AI**.


## 3. GlobMed Dataset

### 📦 Scale & Coverage
- **500,000+ entries**
- **12 languages**, representing ~75% of the global population
  - High-resource: Chinese, English, French, German, Japanese, Korean, Portuguese, Spanish
  - Low-resource: Swahili, Wolof, Yoruba, Zulu

### 🧠 Core Tasks
- **Natural Language Inference (NLI)**
- **Long-form Question Answering (QA)**
- **Multiple-choice Question Answering (MCQA)**

### 📚 Data Sources
- BioNLI, MedNLI  
- ExpertQA-Bio, ExpertQA-Med, LiveQA  
- HeadQA, MedExpQA, MedQA, MMLU-Pro  

All data underwent **manual screening**, **agentic machine translation**, and **bilingual medical expert evaluation** to ensure linguistic accuracy and clinical validity.

## 4. GlobMed-Bench

GlobMed-Bench is the **largest multilingual medical evaluation benchmark to date**.

### 🔍 Evaluation Scope
- **56 state-of-the-art LLMs**
  - 12 proprietary models
  - 44 open-weight models
- **40,000+ independent experiments**
- **125M+ generated responses**

### 📊 Key Findings
- Proprietary LLMs achieve higher average performance but within a narrow range  
- Open-weight LLMs show large variance and strong scaling effects  
- **Severe performance gaps persist in low-resource languages**  
- Reasoning-enhanced LLMs consistently outperform non-reasoning counterparts  


## 5. GlobMed-LLMs

To reduce cross-lingual disparities, we fine-tuned several LLMs on GlobMed.

### 🤖 Models
- MedGemma-4B
- Qwen3 series (1.7B / 4B / 8B)

### 🚀 Results
- **>40% average performance improvement** over baseline models  
- **>3× improvement in low-resource languages**  
- Small models (≤8B) outperform much larger LLMs in multilingual medical tasks  

These results demonstrate that **carefully curated multilingual data can outperform sheer model scale**.


## 6. Data Construction Pipeline

GlobMed was built through a rigorous four-stage pipeline:

1. **Data collection & screening** (manual quality control)  
2. **Agentic machine translation** with medical NER + reflection  
3. **Expert refinement** by dual LLM agents  
4. **Bilingual medical expert evaluation** (accuracy, fluency, completeness)


## 7. Usage

### Load Dataset



## 8. Contact
For any inquiries or concerns, feel free to reach out to us via Email: [Rui Yang](yang.rui@duke-nus.edu.sg) and [xxxxx](xxxxxxxxx).

## 9. Citation
```

```

## 10. License
This repository is licensed under the [MIT](https://github.com/microsoft/PEACE/blob/main/LICENSE) License.
