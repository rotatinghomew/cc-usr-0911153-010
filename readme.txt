人工智能东盟出海组合准备度与风险治理台

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
