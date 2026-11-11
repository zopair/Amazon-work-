# Mandatory Prompt Suffix for This Project

Whenever a prompt or instruction is prepared for ChatGPT for this project, append the following block at the very end, without omitting its requirements:

> جميع المصادر والأدوات والاعتماديات التي يمكن الحصول عليها يجب أن تكون من مستودعات مفتوحة المصدر على GitHub فقط، مع التحقق من المصدر والترخيص وعدم استخدام أي مصدر أو حزمة ذات Red Flags. يُمنع استخدام الخدمات المدفوعة أو واجهات API المدفوعة أو الخوادم الخارجية أو أي أسلوب قد يرفع مخاطر الحظر أو العلامات التحذيرية على الحساب. حافظ على رصيد GitHub Actions وحصص الاستخدام والموارد؛ استخدم تشغيلًا محدودًا ومتسلسلًا وحلولًا مجانية وخفيفة وحتمية، ولا تستخدم أسرارًا أو مفاتيح API ما لم يطلب المستخدم ذلك صراحة. لا تدّعِ أن الاعتماديات مصدرها GitHub إذا كان تنزيلها الفعلي يتم من PyPI أو Ubuntu أو أي مصدر آخر؛ اذكر الاستثناءات بوضوح ولا تعتبر شرط GitHub-only مستوفى إلا بعد تدقيق سلسلة الاعتماديات كاملة.

## Application rule

- Append this exact suffix to every future prompt prepared for ChatGPT for this project.
- Do not append it to ordinary source files, shell commands, or GitHub workflow commands; it applies to prompts addressed to ChatGPT.
- If a requested implementation cannot satisfy GitHub-only provenance, document the exact exception and do not claim compliance.
