人工智能东盟出海组合准备度与风险治理台

共同政策证据：Repository.register_policy 按事件身份保存同一政策证据及修订号，
link_policy_project 将多个项目关联同一事件；open_policy_review 固定项目证据版本、
政策修订和暴露，resolve_policy_review 拒绝在结论前被改过的证据；
policy_impact 可查询跨市场共享的项目和旧尽调。已决旧记录不因政策补报而改写。

运行验收：
python3 -m export_portfolio run --fixture fixtures/acceptance.json --database /tmp/export_portfolio.sqlite3 --output /tmp/export_portfolio-output

核验：
python3 -m export_portfolio verify --database /tmp/export_portfolio.sqlite3 --output /tmp/export_portfolio-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.intake.test_initiative -v

构建检查：
python3 -m compileall -q export_portfolio tests
