"""
GlobalMed Multilingual Prompt Templates

Provides:
1. Prompt templates for 12 languages
2. Answer capture patterns for each language
3. Message generation functions

Migrated from legacy codebase: cmu_nwu_nlp/globalmed/prompt_libs/__init__.py
"""

import string
from typing import Dict, List


# =============================================================================
# PROMPT TEMPLATES - 12 Languages
# =============================================================================
# Each language has 4 templates:
# - bionli_shot: BioNLI with CoT (chain-of-thought)
# - mcqa_shot: MCQA with CoT
# - bionli_da: BioNLI direct answer (no CoT)
# - mcqa_da: MCQA direct answer

PROMPT_LIBS = {
    "en": {
        "bionli_shot": 'TASK: Please determine the relationship between the given premise and hypothesis by selecting the correct option. Think step by step and then finish your answer with "the answer is (X)" where X is the correct letter choice.\n\nPremise:\n{premise}\n\nHypothesis:\n{hypothesis}\n\nOptions:\nA. Entailment\nB. Contradiction\n\nAnswer:',
        "mcqa_shot": 'TASK: Choose the correct answer based on the given question and options. Think step by step and then finish your answer with "the answer is (X)" where X is the correct letter choice.\n\nQuestion:\n{question}\n\nOptions:\n{options}\n\nAnswer:',
        "bionli_da": 'TASK: Please determine the relationship between the given premise and hypothesis by selecting the correct option. Finish your answer with "the answer is (X)" where X is the correct letter choice.\n\nPremise:\n{premise}\n\nHypothesis:\n{hypothesis}\n\nOptions:\nA. Entailment\nB. Contradiction\n\nAnswer:',
        "mcqa_da": 'TASK: Choose the correct answer based on the given question and options. Finish your answer with "the answer is (X)" where X is the correct letter choice.\n\nQuestion:\n{question}\n\nOptions:\n{options}\n\nAnswer:',
    },
    "zh": {
        "bionli_shot": '任务：请通过选择正确的选项来确定给定前提和假设之间的关系。请逐步思考，然后以"答案是(X)"结束您的答案，其中X是正确的字母选择。\n\n前提：\n{premise}\n\n假设：\n{hypothesis}\n\n选项：\nA. 蕴含\nB. 矛盾\n\n答案：',
        "mcqa_shot": '任务：根据所给的问题和选项选择正确答案。请逐步思考，然后以 "答案是(X)" 结尾，其中 X 是正确的字母选项。\n\n问题：\n{question}\n\n选项：\n{options}\n\n回答：',
        "bionli_da": '任务：请通过选择正确的选项来确定给定前提和假设之间的关系。请以"答案是(X)"结束您的答案，其中X是正确的字母选择。\n\n前提：\n{premise}\n\n假设：\n{hypothesis}\n\n选项：\nA. 蕴含\nB. 矛盾\n\n答案：',
        "mcqa_da": '任务：根据所给的问题和选项选择正确答案。请以 "答案是(X)" 结尾，其中 X 是正确的字母选项。\n\n问题：\n{question}\n\n选项：\n{options}\n\n回答：',
    },
    "fr": {
        "bionli_shot": 'TÂCHE: Veuillez déterminer la relation entre la prémisse et l\'hypothèse donnée en sélectionnant l\'option correcte. Réfléchissez étape par étape et terminez votre réponse par "La réponse est (X)" où X est la lettre correspondant au bon choix.\n\nPrémisse:\n{premise}\n\nHypothèse:\n{hypothesis}\n\nOptions:\nA. Implication\nB. Contradiction\n\nRéponse:',
        "mcqa_shot": 'TÂCHE: Choisissez la bonne réponse en vous basant sur la question et les options données. Réfléchissez étape par étape, puis terminez votre réponse par "La réponse est (X)", où X est la correspondant au bon choix.\n\nQuestion:\n{question}\n\nOptions:\n{options}\n\nRéponse:',
        "bionli_da": 'TÂCHE: Veuillez déterminer la relation entre la prémisse et l\'hypothèse donnée en sélectionnant l\'option correcte. Terminez votre réponse par "La réponse est (X)" où X est la lettre correspondant au bon choix.\n\nPrémisse:\n{premise}\n\nHypothèse:\n{hypothesis}\n\nOptions:\nA. Implication\nB. Contradiction\n\nRéponse:',
        "mcqa_da": 'TÂCHE: Choisissez la bonne réponse en vous basant sur la question et les options données. Terminez votre réponse par "La réponse est (X)", où X est la lettre correspondant au bon choix.\n\nQuestion:\n{question}\n\nOptions:\n{options}\n\nRéponse:',
    },
    "de": {
        "bionli_shot": 'AUFGABE: Bitte bestimmen Sie die Beziehung zwischen der gegebenen Prämisse und Hypothese, indem Sie die richtige Option auswählen. Denken Sie Schritt für Schritt und beenden Sie Ihre Antwort mit "Die Antwort ist (X)", wobei X die richtige Buchstabenoption ist.\n\nPrämisse:\n{premise}\n\nHypothese:\n{hypothesis}\n\nOptionen:\nA.Implikation\nB. Widerspruch\n\nAntwort:',
        "mcqa_shot": 'AUFGABE: Bitte wählen Sie die richtige Antwort basierend auf der gestellten Frage und den Optionen. Denken Sie Schritt für Schritt und beenden Sie Ihre Antwort mit "Die Antwort ist (X)", wobei X der richtige Buchstabe ist.\n\nFrage:\n{question}\n\nOptionen:\n{options}\n\nAntwort:',
        "bionli_da": 'AUFGABE: Bitte bestimmen Sie die Beziehung zwischen der gegebenen Prämisse und Hypothese, indem Sie die richtige Option auswählen. Beenden Sie Ihre Antwort mit "Die Antwort ist (X)", wobei X die richtige Buchstabenoption ist.\n\nPrämisse:\n{premise}\n\nHypothese:\n{hypothesis}\n\nOptionen:\nA. Implikation\nB. Widerspruch\n\nAntwort:',
        "mcqa_da": 'AUFGABE: Bitte wählen Sie die richtige Antwort basierend auf der gestellten Frage und den Optionen. Beenden Sie Ihre Antwort mit "Die Antwort ist (X)", wobei X der richtige Buchstabe ist.\n\nFrage:\n{question}\n\nOptionen:\n{options}\n\nAntwort:',
    },
    "ja": {
        "bionli_shot": 'タスク: 与えられた前提と仮説の関係を判断するため、正しい選択肢を選んでください。ステップバイステップで考え、最後に「答えは(X)」と記述してください。Xは正しい選択肢の文字です。\n\n前提：\n{premise}\n\n仮説：\n{hypothesis}\n\n選択肢：\nA. 含意\nB. 矛盾\n\n答え：',
        "mcqa_shot": 'タスク: 与えられた質問と選択肢に基づいて正しい答えを選んでください。ステップバイステップで考え、最後に「答えは(X)」と記述してください。Xは正しい選択肢の文字です。\n\n質問：\n{question}\n\n選択肢：\n{options}\n\n答え：',
        "bionli_da": 'タスク: 与えられた前提と仮説の関係を判断するため、正しい選択肢を選んでください。最後に「答えは(X)」と記述してください。Xは正しい選択肢の文字です。\n\n前提：\n{premise}\n\n仮説：\n{hypothesis}\n\n選択肢：\nA. 含意\nB. 矛盾\n\n答え：',
        "mcqa_da": 'タスク: 与えられた質問と選択肢に基づいて正しい答えを選んでください。最後に「答えは(X)」と記述してください。Xは正しい選択肢の文字です。\n\n質問：\n{question}\n\n選択肢：\n{options}\n\n答え：',
    },
    "ko": {
        "bionli_shot": '작업: 주어진 전제와 가설 사이의 관계를 판단하여, 올바른 선택지를 고르십시오. 단계별로 생각하고 정잡이 "X"일 경우 문자 "답은 (X)입니다"로 답변을 마무리하십시오.\n\n전제:\n{premise}\n\n가설:\n{hypothesis}\n\n선택지:\nA. 함의\nB. 모순\n\n답변:',
        "mcqa_shot": '작업:주어진 질문과 선택지를 바탕으로 정답을 고르십시오. 단계별로 생각하고정답이 "X"일 경우 문자 "답은 (X)입니다"로 답변을 마무리하십시오.\n\n질문:\n{question}\n\n옵션:\n{options}\n\n답변:',
        "bionli_da": '작업: 주어진 전제와 가설 사이의 관계를 판단하여 올바른 선택지를 고르십시오. "답은 (X)입니다"로 답변을 마무리하십시오.\n\n전제:\n{premise}\n\n가설:\n{hypothesis}\n\n선택지:\nA. 함의\nB. 모순\n\n답변:',
        "mcqa_da": '작업: 주어진 질문과 선택지를 바탕으로 정답을 고르십시오. "답은 (X)입니다"로 답변을 마무리하십시오.\n\n질문:\n{question}\n\n옵션:\n{options}\n\n답변:',
    },
    "pt": {
        "bionli_shot": 'TAREFA: Por favor, determine a relação entre a premissa e a hipótese dadas selecionando a opção correta. Pense passo a passo e termine sua resposta com "A resposta é (X)" onde X é a letra da escolha correta.\n\nPremissa:\n{premise}\n\nHipótese:\n{hypothesis}\n\nOpções:\nA. Implicação\nB. Contradição\n\nResposta:',
        "mcqa_shot": 'TAREFA: Escolha a resposta correta com base na pergunta e nas opções fornecidas. Pense passo a passo e finalize sua resposta com "A resposta é (X)", onde X é a letra da escolha correta.\n\nPergunta:\n{question}\n\nOpções:\n{options}\n\nResposta:',
        "bionli_da": 'TAREFA: Por favor, determine a relação entre a premissa e a hipótese dadas selecionando a opção correta. Finalize sua resposta com "A resposta é (X)" onde X é a letra da escolha correta.\n\nPremissa:\n{premise}\n\nHipótese:\n{hypothesis}\n\nOpções:\nA. Implicação\nB. Contradição\n\nResposta:',
        "mcqa_da": 'TAREFA: Escolha a resposta correta com base na pergunta e nas opções fornecidas. Finalize sua resposta com "A resposta é (X)", onde X é a letra da escolha correta.\n\nPergunta:\n{question}\n\nOpções:\n{options}\n\nResposta:',
    },
    "es": {
        "bionli_shot": 'TAREA: Por favor, determine la relación entre la premisa y la hipótesis dadas seleccionando la opción correcta. Piense paso a paso y luego termine su respuesta con "La respuesta es (X)" donde X es la letra de la opción correcta.\n\nPremisa:\n{premise}\n\nHipótesis:\n{hypothesis}\n\nOpciones:\nA. Implicación\nB. Contradicción\n\nRespuesta:',
        "mcqa_shot": 'TAREA: Elige la respuesta correcta según la pregunta y las opciones dadas. Piensa paso a paso y luego termina tu respuesta con "La respuesta es (X)", donde X es la letra de la opción correcta.\n\nPregunta:\n{question}\n\nOpciones:\n{options}\n\nRespuesta:',
        "bionli_da": 'TAREA: Por favor, determine la relación entre la premisa y la hipótesis dadas seleccionando la opción correcta. Termine su respuesta con "La respuesta es (X)" donde X es la letra de la opción correcta.\n\nPremisa:\n{premise}\n\nHipótesis:\n{hypothesis}\n\nOpciones:\nA. Implicación\nB. Contradicción\n\nRespuesta:',
        "mcqa_da": 'TAREA: Elige la respuesta correcta según la pregunta y las opciones dadas. Termina tu respuesta con "La respuesta es (X)", donde X es la letra de la opción correcta.\n\nPregunta:\n{question}\n\nOpciones:\n{options}\n\nRespuesta:',
    },
    "sw": {
        "bionli_shot": 'KAZI: Tafadhali amua uhusiano kati ya hoja iliyotolewa na wazo kwa kuchagua chaguo sahihi. Fikiria hatua kwa hatua na kisha malizia jibu lako na "Jibu ni (X)" ambapo X ni chaguo sahihi cha herufi.\n\nHoja:\n{premise}\n\nWazo:\n{hypothesis}\n\nChaguzi:\nA. Uthibitisho\nB. Kupingana\n\nJibu:',
        "mcqa_shot": 'KAZI: Chagua jibu sahihi kulingana na swali na chaguzi zilizotolewa. Fikiria hatua kwa hatua na kisha malizia jibu lako na "Jibu ni (X)" ambapo X ni chaguo sahihi cha herufi.\n\nSwali:\n{question}\n\nChaguzi:\n{options}\n\nJibu:',
        "bionli_da": 'KAZI: Tafadhali amua uhusiano kati ya hoja iliyotolewa na wazo kwa kuchagua chaguo sahihi. Malizia jibu lako na "Jibu ni (X)" ambapo X ni chaguo sahihi cha herufi.\n\nHoja:\n{premise}\n\nWazo:\n{hypothesis}\n\nChaguzi:\nA. Uthibitisho\nB. Kupingana\n\nJibu:',
        "mcqa_da": 'KAZI: Chagua jibu sahihi kulingana na swali na chaguzi zilizotolewa. Malizia jibu lako na "Jibu ni (X)" ambapo X ni chaguo sahihi cha herufi.\n\nSwali:\n{question}\n\nChaguzi:\n{options}\n\nJibu:',
    },
    "wo": {
        "bionli_shot": 'LIGGÉEY: Jërëjëfël na nga xelal diggante bi nekk ci digle bi ak njortu bi ci tann ci option yi dëgg. Xalaat ci ay xeeti waxtaan te nga jeexal sa tontu ak "Tontu bi mooy (X)" fu X di araf bi dëgg.\n\nDigle:\n{premise}\n\nNjortu:\n{hypothesis}\n\nOptions:\nA. Jagleel\nB. Dëddu\n\nTontu:',
        "mcqa_shot": 'LIGGÉEY: Tànnal tontu bi dëgg ci li ñu laaj ak tànneefi yi. Xalaat ci ay xeeti waxtaan te nga jeexal sa tontu ak "Tontu bi mooy (X)" fu X di araf bi dëgg.\n\nLaaj:\n{question}\n\nTànneefi:\n{options}\n\nTontu:',
        "bionli_da": 'LIGGÉEY: Jërëjëfël na nga xelal diggante bi nekk ci digle bi ak njortu bi ci tann ci option yi dëgg. Nga jeexal sa tontu ak "Tontu bi mooy (X)" fu X di araf bi dëgg.\n\nDigle:\n{premise}\n\nNjortu:\n{hypothesis}\n\nOptions:\nA. Jagleel\nB. Dëddu\n\nTontu:',
        "mcqa_da": 'LIGGÉEY: Tànnal tontu bi dëgg ci li ñu laaj ak tànneefi yi. Nga jeexal sa tontu ak "Tontu bi mooy (X)" fu X di araf bi dëgg.\n\nLaaj:\n{question}\n\nTànneefi:\n{options}\n\nTontu:',
    },
    "yo": {
        "bionli_shot": 'IṢẸ́: Jọwọ pinnu ìbátan láàrin ìsẹ̀lẹ̀ tí a fún ọ àti ìbéèrè nípa yíyan àṣàyàn tó tọ́. Ronu lọ́nà tó péye kí o sì parí ìdáhùn rẹ pẹ̀lú "Ìdáhùn náà ni (X)" níbi tí X jẹ́ àṣàyàn lẹ́tà tó tọ́.\n\nÌsẹ̀lẹ̀:\n{premise}\n\nÌbéèrè:\n{hypothesis}\n\nÀwọn àṣàyàn:\nA. Ìbámu\nB. Ìlòdì\n\nÌdáhùn:',
        "mcqa_shot": 'IṢẸ́: Yan ìdáhùn tó tọ́ lórí ìbéèrè àti àwọn àṣàyàn tí a fún ọ. Ronu lọ́nà tó péye kí o sì parí ìdáhùn rẹ pẹ̀lú "Ìdáhùn náà ni (X)" níbi tí X jẹ́ àṣàyàn lẹ́tà tó tọ́.\n\nÌbéèrè:\n{question}\n\nÀwọn àṣàyàn:\n{options}\n\nÌdáhùn:',
        "bionli_da": 'IṢẸ́: Jọwọ pinnu ìbátan láàrin ìsẹ̀lẹ̀ tí a fún ọ àti ìbéèrè nípa yíyan àṣàyàn tó tọ́. Parí ìdáhùn rẹ pẹ̀lú "Ìdáhùn náà ni (X)" níbi tí X jẹ́ àṣàyàn lẹ́tà tó tọ́.\n\nÌsẹ̀lẹ̀:\n{premise}\n\nÌbéèrè:\n{hypothesis}\n\nÀwọn àṣàyàn:\nA. Ìbámu\nB. Ìlòdì\n\nÌdáhùn:',
        "mcqa_da": 'IṢẸ́: Yan ìdáhùn tó tọ́ lórí ìbéèrè àti àwọn àṣàyàn tí a fún ọ. Parí ìdáhùn rẹ pẹ̀lú "Ìdáhùn náà ni (X)" níbi tí X jẹ́ àṣàyàn lẹ́tà tó tọ́.\n\nÌbéèrè:\n{question}\n\nÀwọn àṣàyàn:\n{options}\n\nÌdáhùn:',
    },
    "zu": {
        "bionli_shot": 'UMSEBENZI: Sicela unqume ubudlelwano phakathi kwesitatimende esinikeziwe kanye nomqondo ngokukhetha inketho efanele. Cabanga ngezigaba futhi uqede impendulo yakho ngo-"Impendulo ithi (X)" lapho u-X eyinketho encwadi efanele.\n\nIsitatimende:\n{premise}\n\nUmqondo:\n{hypothesis}\n\nIzinketho:\nA. Ukuvumelana\nB. Ukuphikisana\n\nImpendulo:',
        "mcqa_shot": 'UMSEBENZI: Khetha impendulo efanele ngokusekelwe kumbuzo kanye nezinketho ezinikeziwe. Cabanga ngezigaba futhi uqede impendulo yakho ngo-"Impendulo ithi (X)" lapho u-X eyinketho encwadi efanele.\n\nUmbuzo:\n{question}\n\nIzinketho:\n{options}\n\nImpendulo:',
        "bionli_da": 'UMSEBENZI: Sicela unqume ubudlelwano phakathi kwesitatimende esinikeziwe kanye nomqondo ngokukhetha inketho efanele. Qeda impendulo yakho ngo-"Impendulo ithi (X)" lapho u-X eyinketho encwadi efanele.\n\nIsitatimende:\n{premise}\n\nUmqondo:\n{hypothesis}\n\nIzinketho:\nA. Ukuvumelana\nB. Ukuphikisana\n\nImpendulo:',
        "mcqa_da": 'UMSEBENZI: Khetha impendulo efanele ngokusekelwe kumbuzo kanye nezinketho ezinikeziwe. Qeda impendulo yakho ngo-"Impendulo ithi (X)" lapho u-X eyinketho encwadi efanele.\n\nUmbuzo:\n{question}\n\nIzinketho:\n{options}\n\nImpendulo:',
    },
}


# =============================================================================
# ANSWER CAPTURE PATTERNS - For regex-based extraction fallback
# =============================================================================
# Used when lighteval extraction fails (especially for low-resource languages)

ANSWER_CAPTURE_PATTERNS = {
    "en": r"the answer is \(?([ABCDEFGHIJ])\)?",
    "zh": r"答案是\(?([ABCDEFGHIJ])\)?",
    "fr": r"La réponse est \(?([ABCDEFGHIJ])\)?",
    "de": r"Die Antwort ist \(?([ABCDEFGHIJ])\)?",
    "ja": r"答えは\(?([ABCDEFGHIJ])\)?",
    "ko": r"답은 \(?([ABCDEFGHIJ])\)?입니다",
    "pt": r"A resposta é \(?([ABCDEFGHIJ])\)?",
    "es": r"La respuesta es \(?([ABCDEFGHIJ])\)?",
    "sw": r"Jibu ni \(?([ABCDEFGHIJ])\)?",
    "wo": r"Tontu bi mooy \(?([ABCDEFGHIJ])\)?",
    "yo": r"Ìdáhùn náà ni \(?([ABCDEFGHIJ])\)?",
    "zu": r"Impendulo ithi \(?([ABCDEFGHIJ])\)?",
}


# =============================================================================
# MESSAGE GENERATION FUNCTIONS
# =============================================================================

def get_message_from_doc(
    doc: Dict,
    subset: str,
    lang: str,
    prompt_style: str = "shot"
) -> List[Dict[str, str]]:
    """
    Generate a message list from a data document.

    This function follows the exact logic from the legacy codebase
    (cmu_nwu_nlp/globalmed/utils.py:get_message_from_doc).

    Args:
        doc: Data document containing question/premise/hypothesis and options
        subset: Dataset name (MedQA, HeadQA, MedExpQA, MMLU-Pro, BioNLI)
        lang: Language code (en, zh, fr, de, ja, ko, pt, es, sw, wo, yo, zu)
        prompt_style: Prompt style - "shot" (with CoT) or "da" (direct answer)

    Returns:
        List of message dicts in OpenAI format: [{"role": "user", "content": "..."}]
    """
    if subset == "MedNLI":
        from globalmed.mednli_prompts import MEDNLI_PROMPTS
        if prompt_style != "da":
            raise ValueError("The SI MedNLI templates use direct answers. Select --prompt_style da.")
        return [{"role": "user", "content": MEDNLI_PROMPTS[lang].format(
            premise=doc["premise"], hypothesis=doc["hypothesis"])}]
    if "nli" in subset.lower():
        # NLI task (BioNLI)
        prompt_key = f"{subset.lower()}_{prompt_style}"
        prompt_template = PROMPT_LIBS[lang][prompt_key]

        # Validate template has required placeholders
        assert "{premise}" in prompt_template and "{hypothesis}" in prompt_template, \
            f"Invalid NLI template for {subset}, {prompt_style}, {lang}"

        prompt_text = prompt_template.format(
            premise=doc["premise"],
            hypothesis=doc["hypothesis"]
        )
    else:
        # MCQA task
        prompt_template = PROMPT_LIBS[lang][f"mcqa_{prompt_style}"]

        # Get options text
        if "options" in doc:
            # New format: options is a dict {A: ..., B: ...}
            options_text = "\n".join([f"{k}. {v}" for k, v in doc["options"].items()])
            question = doc["question"]
        else:
            # Legacy format: Option1, Option2, ...
            # Determine number of options based on subset
            if subset in ["MedQA", "HeadQA"]:
                opt_num = 4
            elif subset == "MedExpQA":
                opt_num = 5
            elif subset == "MMLU-Pro":
                opt_num = 10
            else:
                opt_num = 4  # Default

            options_text = "\n".join(
                [f"{string.ascii_uppercase[i]}. {doc[f'Option{i + 1}']}"
                 for i in range(opt_num) if isinstance(doc.get(f'Option{i + 1}'), str)]
            )
            question = doc.get("Question", doc.get("question", ""))

        # Validate template has required placeholders
        assert "{question}" in prompt_template and "{options}" in prompt_template, \
            f"Invalid MCQA template for {subset}, {prompt_style}, {lang}"

        prompt_text = prompt_template.format(
            question=question,
            options=options_text
        )

    return [{"role": "user", "content": prompt_text}]


def get_prompt_text(
    doc: Dict,
    subset: str,
    lang: str,
    prompt_style: str = "shot"
) -> str:
    """
    Get the prompt text directly (without message wrapper).

    Args:
        doc: Data document
        subset: Dataset name
        lang: Language code
        prompt_style: Prompt style

    Returns:
        Prompt text string
    """
    messages = get_message_from_doc(doc, subset, lang, prompt_style)
    return messages[0]["content"]


def get_supported_languages() -> List[str]:
    """Get list of all supported languages."""
    return list(PROMPT_LIBS.keys())
