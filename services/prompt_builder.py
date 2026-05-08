from typing import Optional, Dict


# Language code to full name mapping
LANGUAGE_NAMES = {
    "zh": "Chinese",
    "en": "English",
    "fr": "French",
    "pt": "Portuguese",
    "es": "Spanish",
    "ja": "Japanese",
    "tr": "Turkish",
    "ru": "Russian",
    "ar": "Arabic",
    "ko": "Korean",
    "th": "Thai",
    "it": "Italian",
    "de": "German",
    "vi": "Vietnamese",
    "ms": "Malay",
    "id": "Indonesian",
    "tl": "Filipino",
    "hi": "Hindi",
    "zh-Hant": "Traditional Chinese",
    "pl": "Polish",
    "cs": "Czech",
    "nl": "Dutch",
    "km": "Khmer",
    "my": "Burmese",
    "fa": "Persian",
    "gu": "Gujarati",
    "ur": "Urdu",
    "te": "Telugu",
    "mr": "Marathi",
    "he": "Hebrew",
    "bn": "Bengali",
    "ta": "Tamil",
    "uk": "Ukrainian",
    "bo": "Tibetan",
    "kk": "Kazakh",
    "mn": "Mongolian",
    "ug": "Uyghur",
    "yue": "Cantonese",
}


class PromptBuilder:
    """Builds translation prompts based on language pairs and options"""

    def __init__(self):
        self.language_names = LANGUAGE_NAMES

    def build_translation_prompt(
        self,
        source_text: str,
        source_lang: str,
        target_lang: str,
        terminology: Optional[Dict[str, str]] = None,
        context: Optional[str] = None,
        preserve_format: bool = False,
    ) -> str:
        """
        Build a translation prompt based on language pair and options.

        Args:
            source_text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            terminology: Optional terminology mapping
            context: Optional context information
            preserve_format: Whether to preserve formatting

        Returns:
            Formatted prompt string
        """
        # Get full language names
        target_language = self.language_names.get(target_lang, target_lang)

        # Determine if we should use Chinese or English template
        use_chinese_template = source_lang in ["zh", "zh-Hant"] or target_lang in ["zh", "zh-Hant"]

        # Wrap text in format preservation tags if needed
        if preserve_format:
            source_text = f"<preserve_format>\n{source_text}\n</preserve_format>"

        # Build the prompt based on template and options
        if use_chinese_template:
            return self._build_chinese_prompt(
                source_text, target_language, terminology, context
            )
        else:
            return self._build_english_prompt(
                source_text, target_language, terminology, context
            )

    def _build_chinese_prompt(
        self,
        source_text: str,
        target_language: str,
        terminology: Optional[Dict[str, str]],
        context: Optional[str],
    ) -> str:
        """Build prompt using Chinese template"""
        parts = []

        # Add terminology if provided
        if terminology:
            parts.append("参考下面的翻译：")
            for source_term, target_term in terminology.items():
                parts.append(f"{source_term} 翻译成 {target_term}")
            parts.append("")

        # Add context if provided
        if context:
            parts.append(context)
            parts.append(f"参考上面的信息，把下面的文本翻译成{target_language}，注意不需要翻译上文，也不要额外解释：")
        else:
            parts.append(f"将以下文本翻译为{target_language}，注意只需要输出翻译后的结果，不要额外解释：")

        parts.append(source_text)

        return "\n".join(parts)

    def _build_english_prompt(
        self,
        source_text: str,
        target_language: str,
        terminology: Optional[Dict[str, str]],
        context: Optional[str],
    ) -> str:
        """Build prompt using English template"""
        parts = []

        # Add terminology if provided
        if terminology:
            parts.append("Terminology reference:")
            for source_term, target_term in terminology.items():
                parts.append(f"- {source_term} → {target_term}")
            parts.append("")

        # Add context if provided
        if context:
            parts.append(f"Context: {context}")
            parts.append("")

        parts.append(f"Translate the following segment into {target_language}, without additional explanation.")
        parts.append("")
        parts.append(source_text)

        return "\n".join(parts)
