# Skill Pay 一次性购买 / Skill Pay One-Time Purchase

[简体中文](#简体中文) | [English](#english)

## 简体中文

### 产品边界

支付宝 Skill Pay 面向 Skill 服务商，支付、商品销售与交付由 Skill Pay 平台承接。本仓库不需要、也不应加入 Vibe Pay 网页收款 SDK 或虚构的 Skill Pay 支付 API。Skill Pay 的商品提交、签约、定价、审核和上架，需要在 [Skill Pay 开发者门户](https://skillpay.alipay.com/creator/products?aipay_choose_perspective=creator) 中按账号当前开放的流程完成。

官方 Skill Pay 首页说明：一次性付费后，购买者会获得 Skill 明文；周期付费只提供当期使用权，不交付明文，也不会自动续费。Skill 上架前需要通过安全检测；提交商品前需签署 Skill Pay 和 AI 按量付费协议。开放范围、价格规则、协议要求和审核结果以登录后的官方门户及协议为准。

### 本仓库的发布限制

当前 GitHub 仓库为公开仓库，并采用 MIT 许可证。MIT 允许他人使用、修改、分发和销售代码；任何人都能直接获取仓库中的 Skill 文件。因而，将相同内容提交为一次性付费商品不会形成代码访问控制或独占交付。若要把明文 Skill 作为付费商品销售，发布者应先决定是否继续公开同一份内容；门户商品链接和购买流程也应明确说明买家实际获得的内容。

不要在仓库或 Skill 包中放入支付宝密钥、个人资料、真实业务数据、私有地址或其他不适合交付给购买者的内容。一次性购买会交付明文，提交前应按此标准审阅完整包。

### 提交前检查

1. 在 Skill Pay 开发者门户确认主体准入、签约协议、商品要求、售卖模式和当期定价规则。
2. 审阅 Skill、引用文件、示例和许可证，确认全部内容可明文交付且具有相应分发权。
3. 在仓库根目录运行 `python scripts/test_skill.py` 和 `python -m unittest discover -s tests -v`。
4. 在 `dist/` 下生成 ZIP，并检查其内容与待提交版本一致：

   ```powershell
   python scripts/test_skill.py --package dist/distributed-system-audit-skillpay.zip
   ```

   打包器不会覆盖已有 ZIP；若文件已存在，请换一个输出文件名。
5. 按门户当前支持的格式上传商品文件（本仓库 ZIP 是待核验的候选包，不代表已验证门户兼容），填写商品说明和价格，完成安全检测及上架审核。
6. 商品正式上架后，再把门户提供的商品页链接补充到中英文 README；不要预先声称商品已上架或支付已联调。

### 官方资料

- [Skill Pay 官方网站](https://skillpay.alipay.com/)
- [支付宝 AI 付产品概览中的 Skill Pay 说明](https://aipay.alipay.com/docs/overview.html)
- [Skill Pay 开发者商品门户](https://skillpay.alipay.com/creator/products?aipay_choose_perspective=creator)

## English

### Product boundary

Alipay Skill Pay serves Skill providers and handles payment, product sales, and delivery through its platform. This repository does not need a Vibe Pay web checkout SDK or an invented Skill Pay payment API. Submit, sign, price, review, and publish the product through the [Skill Pay developer portal](https://skillpay.alipay.com/creator/products?aipay_choose_perspective=creator), following the workflow currently available to your account.

The official Skill Pay homepage says a one-time purchase gives the buyer the Skill in plaintext. A subscription grants access for the current term, does not deliver plaintext, and does not renew automatically. Skills must pass security checks before listing, and the platform requires the Skill Pay and AI Pay-per-use agreements before product submission. Confirm eligibility, pricing, agreements, and review status in the signed-in portal and current agreements.

### Publication constraint for this repository

This GitHub repository is public and uses the MIT License. MIT permits others to use, modify, distribute, and sell the code, and anyone can download the Skill files from the repository. Listing the same content as a one-time purchase therefore does not provide code access control or exclusive delivery. Before selling the plaintext Skill, decide whether the same content will remain public; describe clearly what buyers receive on the product page.

Do not include Alipay credentials, personal data, real business data, private endpoints, or other material that should not be delivered to buyers in the repository or Skill package. Review the complete package with plaintext delivery in mind.

### Pre-submission checklist

1. Confirm merchant eligibility, agreements, product requirements, sale mode, and current pricing rules in the Skill Pay developer portal.
2. Review the Skill, references, examples, and license to confirm the full contents can be delivered in plaintext and are cleared for distribution.
3. From the repository root, run `python scripts/test_skill.py` and `python -m unittest discover -s tests -v`.
4. Create a ZIP under `dist/` and verify it matches the intended submission:

   ```powershell
   python scripts/test_skill.py --package dist/distributed-system-audit-skillpay.zip
   ```

   The packager will not overwrite an existing ZIP; choose another filename if needed.
5. Upload the product in the format currently accepted by the portal (this repository ZIP is a candidate package, not proof of portal compatibility), enter the required description and price, and complete security review and listing approval.
6. Add the product page link to both READMEs only after the listing is live. Do not claim that listing or payment integration is complete beforehand.

### Official references

- [Skill Pay official website](https://skillpay.alipay.com/)
- [Skill Pay in the Alipay AI Pay product overview](https://aipay.alipay.com/docs/overview.html)
- [Skill Pay developer product portal](https://skillpay.alipay.com/creator/products?aipay_choose_perspective=creator)
