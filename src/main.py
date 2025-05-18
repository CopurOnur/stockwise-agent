"""Entry point for Stock‑Wise Agent MVP."""

from agents.data_agent import DataAgent
from agents.news_agent import NewsAgent
from agents.report_agent import ReportAgent

def main():
    data = DataAgent().run()
    news = NewsAgent().run()
    ReportAgent().run(data, news)

if __name__ == "__main__":
    main()
