人工智能东盟出海组合准备度与风险治理台

共同政策证据：Repository.register_policy 按事件身份保存同一政策证据及修订号，
link_policy_project 将多个项目关联同一事件；open_policy_review 固定项目证据版本、
政策修订和暴露，resolve_policy_review 拒绝在结论前被改过的证据；
policy_impact 可查询跨市场共享的项目和旧尽调。已决旧记录不因政策补报而改写。

关联风险归因：Repository.register_policy_shock 把一次市场冲击固定在单一事件身份上
（observed/bounded），register_association_judgment 登记项目-事件联系，分四桶呈现：
project_specific（单项目波动）、shared_observed（有证据支持且经已决评审固定的共同冲击）、
shared_bounded（只有上下界的待决联系，给区间不给点估计）、unidentified（缺共同观测，
保留不确定性）。risk_attribution 输出各项目对组合压力损失的贡献，四桶拆分与项目总损失
精确对账；同一事件在组合层只计一次，不重复计为多份独立证据。evidence_correction_impact
在补报/纠正证据时指出受影响的待审评审与项目，并把已决评审列为冻结口径。归因结果写入
董事会材料 risk-attribution.json（含哈希校验）；只解释和复核现有暴露，不挑选项目组合、
不改变预算分配，也不因重算改变任何项目阶段。

运行验收：
python3 -m export_portfolio run --fixture fixtures/acceptance.json --database /tmp/export_portfolio.sqlite3 --output /tmp/export_portfolio-output

核验：
python3 -m export_portfolio verify --database /tmp/export_portfolio.sqlite3 --output /tmp/export_portfolio-output

关联风险归因与证据补报影响：
python3 -m export_portfolio attribute --database /tmp/export_portfolio.sqlite3
python3 -m export_portfolio correction-impact --database /tmp/export_portfolio.sqlite3 --event <event_id>

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.intake.test_initiative -v
python3 -m unittest tests.governance.test_risk_attribution -v

构建检查：
python3 -m compileall -q export_portfolio tests
