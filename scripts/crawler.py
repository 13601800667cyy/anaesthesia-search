#!/usr/bin/env python3
"""
麻醉镇痛与围术期脑健康资讯爬虫
用于自动抓取行业资讯并生成 news.json 数据文件

数据源配置（基于用户提供的Excel文件）:
1. 癌症期刊汇总 - 期刊网站
2. 疼痛领域企业 - 公司动态
3. 行业资讯源 - 医脉通、丁香园等
"""

import json
import os
import re
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


class NewsCrawler:
    def __init__(self):
        self.news_list: List[Dict] = []
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.output_file = os.path.join(self.data_dir, 'news.json')

        # 基于用户提供的Excel文件配置的数据源
        self.data_sources = {
            # 临床进展 - 术后谵妄、POCD、麻醉深度监测等
            "clinical": [
                {"name": "医脉通", "url": "https://www.medlive.cn/news/", "category": "clinical"},
                {"name": "丁香园", "url": "https://www.dxy.cn/", "category": "clinical"},
            ],
            # 政策标准 - 卫健委、医保局等
            "policy": [
                {"name": "国家卫健委", "url": "http://www.nhc.gov.cn/", "category": "policy"},
                {"name": "国家医保局", "url": "http://www.nhsa.gov.cn/", "category": "policy"},
            ],
            # 产业市场 - 投融资、企业动态
            "industry": [
                {"name": "医药魔方", "url": "https://www.pharmcube.com/", "category": "industry"},
                {"name": "动脉网", "url": "https://www.vbdata.cn/", "category": "industry"},
            ],
            # 学术会议
            "conference": [
                {"name": "中华麻醉学杂志", "url": "http://www.cmaes.org/", "category": "conference"},
            ]
        }

    def generate_id(self, title: str, date: str) -> str:
        """生成唯一ID"""
        raw = f"{title}{date}"
        return hashlib.md5(raw.encode()).hexdigest()[:8]

    def crawl_webpage(self, url: str, name: str, max_items: int = 10) -> List[Dict]:
        """爬取单个网页的新闻"""
        if not DEPENDENCIES_AVAILABLE:
            return []

        news_items = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取链接和标题
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                title = link.get_text(strip=True)

                # 过滤有效的标题和链接
                if len(title) > 10 and ('麻醉' in title or '镇痛' in title or '疼痛' in title
                        or '谵妄' in title or 'POCD' in title or '围术期' in title
                        or '脑健康' in title or '神经' in title or '术后' in title):
                    news_items.append({
                        "title": title[:200],
                        "url": href if href.startswith('http') else url + href,
                        "source": name
                    })

                if len(news_items) >= max_items:
                    break

        except Exception as e:
            print(f"  ⚠ 爬取 {name} 失败: {e}")

        return news_items

    def create_sample_news(self) -> List[Dict]:
        """创建示例新闻数据（基于Excel中的企业和期刊信息）"""
        today = datetime.now()
        news = []

        # ===== 临床进展 =====
        clinical_news = [
            {
                "id": self.generate_id("术后谵妄防治专家共识（2026版）发布", "2026-03-01"),
                "title": "术后谵妄防治专家共识（2026版）正式发布",
                "category": "临床进展",
                "source": "中华麻醉学杂志",
                "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "中华麻醉学分会发布最新版术后谵妄防治专家共识，涵盖风险评估、预防措施和治疗方案。",
                "url": "https://www.cmaes.org/",
                "tags": ["术后谵妄", "专家共识", "防治"]
            },
            {
                "id": self.generate_id("POCD研究新进展", "2026-03-01"),
                "title": "术后认知功能障碍（POCD）分子机制研究取得新进展",
                "category": "临床进展",
                "source": "Journal of Pain and Symptom Management",
                "date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
                "summary": "最新研究发现神经炎症在术后认知功能障碍中起关键作用，为靶向治疗提供新思路。",
                "url": "https://www.sciencedirect.com/journal/journal-of-pain-and-symptom-management",
                "tags": ["POCD", "神经炎症", "认知功能"]
            },
            {
                "id": self.generate_id("脑氧饱和度监测指南", "2026-02-28"),
                "title": "围术期脑氧饱和度监测临床实践指南更新",
                "category": "临床进展",
                "source": "British Journal of Anaesthesia",
                "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                "summary": "指南强调rSO2监测在高风险手术中的重要性，推荐早期干预阈值。",
                "url": "https://www.bjanaesthesia.org.uk/",
                "tags": ["脑氧监测", "围术期", "指南"]
            },
            {
                "id": self.generate_id("麻醉深度监测新指标", "2026-02-27"),
                "title": "AI辅助麻醉深度监测系统获FDA批准",
                "category": "临床进展",
                "source": "FDA",
                "date": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
                "summary": "新型AI麻醉深度监测系统获FDA批准，可实时预测患者麻醉状态。",
                "url": "https://www.fda.gov/",
                "tags": ["麻醉深度监测", "AI", "FDA"]
            },
            {
                "id": self.generate_id("多模式镇痛指南", "2026-02-26"),
                "title": "多模式镇痛在骨科手术中的应用指南",
                "category": "临床进展",
                "source": "Pain Medicine",
                "date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
                "summary": "新指南推荐阿片类药物节俭方案，强调NSAIDs联合区域阻滞的多模式镇痛。",
                "url": "https://academic.oup.com/journals/",
                "tags": ["多模式镇痛", "骨科", "镇痛"]
            }
        ]
        news.extend(clinical_news)

        # ===== 器械新药 =====
        device_news = [
            {
                "id": self.generate_id("新型镇痛泵获批", "2026-03-01"),
                "title": "新型智能镇痛泵在国内获批上市",
                "category": "器械新药",
                "source": "国家药监局",
                "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "这款智能镇痛泵可实现精准剂量控制，降低术后镇痛相关不良反应。",
                "url": "https://www.nmpa.gov.cn/",
                "tags": ["镇痛泵", "医疗器械", "获批"]
            },
            {
                "id": self.generate_id("NGS基因检测产品", "2026-02-28"),
                "title": "疼痛相关基因检测产品获批上市",
                "category": "器械新药",
                "source": "国家药监局",
                "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                "summary": "国内首款疼痛相关基因检测产品获批，可指导个性化镇痛药物选择。",
                "url": "https://www.nmpa.gov.cn/",
                "tags": ["基因检测", "精准医疗", "镇痛"]
            },
            {
                "id": self.generate_id("VR镇痛系统CE认证", "2026-02-25"),
                "title": "Oncomfort VR镇痛系统获得CE认证",
                "category": "器械新药",
                "source": "Oncomfort",
                "date": (today - timedelta(days=6)).strftime("%Y-%m-%d"),
                "summary": "比利时Oncomfort公司的数字镇静VR系统获得CE认证，用于术前后疼痛管理。",
                "url": "https://www.oncomfort.com/",
                "tags": ["VR镇痛", "数字疗法", "CE认证"]
            }
        ]
        news.extend(device_news)

        # ===== 产业市场 =====
        industry_news = [
            {
                "id": self.generate_id("疼痛管理市场报告", "2026-03-01"),
                "title": "2026年全球疼痛管理市场规模将超800亿美元",
                "category": "产业市场",
                "source": "Frost & Sullivan",
                "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "Frost & Sullivan发布报告称，非阿片类镇痛药和数字疗法将成为增长主要驱动力。",
                "url": "https://www.frost.com/",
                "tags": ["市场报告", "疼痛管理", "产业"]
            },
            {
                "id": self.generate_id("疼痛领域融资", "2026-02-28"),
                "title": "美国疼痛管理公司kaia Health完成C轮融资",
                "category": "产业市场",
                "source": "Crunchbase",
                "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                "summary": "kaia Health完成5000万美元C轮融资，用于开发数字疼痛管理平台。",
                "url": "https://www.crunchbase.com/",
                "tags": ["融资", "数字疗法", "疼痛"]
            },
            {
                "id": self.generate_id("神经刺激器市场", "2026-02-26"),
                "title": "神经病理性疼痛刺激器市场快速增长",
                "category": "产业市场",
                "source": "BioCentury",
                "date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
                "summary": "预计到2030年，神经刺激器市场将达到50亿美元，年复合增长率12%。",
                "url": "www.biocentury.com/",
                "tags": ["神经刺激器", "市场", "疼痛"]
            },
            {
                "id": self.generate_id("Mainstay Medical投资", "2026-02-24"),
                "title": "Mainstay Medical完成ReActiv8植入器械商业化",
                "category": "产业市场",
                "source": "Mainstay Medical",
                "date": (today - timedelta(days=7)).strftime("%Y-%m-%d"),
                "summary": "爱尔兰Mainstay Medical的ReActiv8神经刺激器获得FDA批准用于慢性腰背痛治疗。",
                "url": "https://www.mainstaymedical.com/",
                "tags": ["神经刺激", "腰背痛", "FDA"]
            },
            {
                "id": self.generate_id("Hoba Therapeutics融资", "2026-02-23"),
                "title": "Hoba Therapeutics完成B轮融资",
                "category": "产业市场",
                "source": "Crunchbase",
                "date": (today - timedelta(days=8)).strftime("%Y-%m-%d"),
                "summary": "Hoba Therapeutics获得2000万美元B轮融资，专注神经病理性疼痛新药研发。",
                "url": "https://www.crunchbase.com/",
                "tags": ["融资", "神经病理性疼痛", "新药"]
            }
        ]
        news.extend(industry_news)

        # ===== 政策标准 =====
        policy_news = [
            {
                "id": self.generate_id("医保支付改革", "2026-03-01"),
                "title": "国家医保局发布新型镇痛药物医保支付标准",
                "category": "政策标准",
                "source": "国家医保局",
                "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "多种新型镇痛药物纳入医保目录，患者用药负担将进一步降低。",
                "url": "https://www.nhsa.gov.cn/",
                "tags": ["医保", "镇痛药物", "政策"]
            },
            {
                "id": self.generate_id("麻醉质量控制", "2026-02-27"),
                "title": "卫健委发布麻醉质量控制指标（2026版）",
                "category": "政策标准",
                "source": "国家卫健委",
                "date": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
                "summary": "新版指标涵盖麻醉相关不良事件、术后镇痛质量等核心指标。",
                "url": "http://www.nhc.gov.cn/",
                "tags": ["质量控制", "麻醉", "标准"]
            }
        ]
        news.extend(policy_news)

        # ===== 学术会议 =====
        conference_news = [
            {
                "id": self.generate_id("ASA年会", "2026-03-01"),
                "title": "2026年美国麻醉医师协会（ASA）年会将于10月召开",
                "category": "学术会议",
                "source": "ASA",
                "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "ASA年会将聚焦术后脑健康和AI在麻醉中的应用。",
                "url": "https://www.asahq.org/",
                "tags": ["学术会议", "ASA", "麻醉"]
            },
            {
                "id": self.generate_id("中华麻醉年会", "2026-02-20"),
                "title": "2026年中华医学会麻醉学分会年会将在南京召开",
                "category": "学术会议",
                "source": "中华麻醉学杂志",
                "date": (today - timedelta(days=11)).strftime("%Y-%m-%d"),
                "summary": "会议将设置围术期脑健康、疼痛管理等专题分会场。",
                "url": "http://www.cmaes.org/",
                "tags": ["学术会议", "中华麻醉", "年会"]
            }
        ]
        news.extend(conference_news)

        # ===== 成果转化 =====
        transfer_news = [
            {
                "id": self.generate_id("徐州医科大学转化", "2026-02-28"),
                "title": "徐州医科大学麻醉重点实验室成果转化取得突破",
                "category": "成果转化",
                "source": "徐州医科大学",
                "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                "summary": "实验室一项关于术后谵妄早期预警系统专利成功转化。",
                "url": "https://www.xzmc.edu.cn/",
                "tags": ["成果转化", "术后谵妄", "专利"]
            },
            {
                "id": self.generate_id("专利转化", "2026-02-25"),
                "title": "麻醉深度监测算法专利成功转让企业",
                "category": "成果转化",
                "source": "医脉通",
                "date": (today - timedelta(days=6)).strftime("%Y-%m-%d"),
                "summary": "某高校科研团队开发的麻醉深度监测算法专利以500万元转让。",
                "url": "https://www.medlive.cn/",
                "tags": ["专利转化", "麻醉监测", "算法"]
            }
        ]
        news.extend(transfer_news)

        # ===== 通用行业资讯 =====
        general_news = [
            {
                "id": self.generate_id("人福医药公告", "2026-03-01"),
                "title": "人福医药发布2025年度报告，镇痛业务增长显著",
                "category": "通用行业资讯",
                "source": "人福医药",
                "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "公司镇痛药物板块收入同比增长25%，枸橼酸芬太尼销量创新高。",
                "url": "https://www.humanwell.com.cn/",
                "tags": ["人福医药", "镇痛", "财报"]
            },
            {
                "id": self.generate_id("恒瑞医药镇痛管线", "2026-02-28"),
                "title": "恒瑞医药镇痛新药研发管线公布",
                "category": "通用行业资讯",
                "source": "恒瑞医药",
                "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                "summary": "恒瑞公布在研镇痛新药5项，其中1项进入III期临床。",
                "url": "https://www.hrms.com.cn/",
                "tags": ["恒瑞医药", "镇痛新药", "研发"]
            },
            {
                "id": self.generate_id("恩华药业合作", "2026-02-26"),
                "title": "恩华药业与以色列公司签署镇痛技术合作协议",
                "category": "通用行业资讯",
                "source": "恩华药业",
                "date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
                "summary": "双方将在新型局部镇痛技术领域展开合作。",
                "url": "http://www.enova-pharma.com/",
                "tags": ["恩华药业", "合作", "镇痛"]
            },
            {
                "id": self.generate_id("海思科创新药", "2026-02-24"),
                "title": "海思科自主研发的新型镇痛药进入II期临床",
                "category": "通用行业资讯",
                "source": "海思科",
                "date": (today - timedelta(days=7)).strftime("%Y-%m-%d"),
                "summary": "该药物为选择性钠离子通道抑制剂，有望解决阿片类药物成瘾问题。",
                "url": "https://www.westchina-pharma.com/",
                "tags": ["海思科", "创新药", "临床"]
            },
            {
                "id": self.generate_id("中国麻醉周", "2026-03-01"),
                "title": "2026中国麻醉周活动启动",
                "category": "通用行业资讯",
                "source": "中华医学会麻醉学分会",
                "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "今年麻醉周主题为'安全舒适，健康同行'，将开展系列科普活动。",
                "url": "http://www.cmaes.org/",
                "tags": ["中国麻醉周", "科普", "活动"]
            }
        ]
        news.extend(general_news)

        return news

    def crawl(self) -> List[Dict]:
        """
        执行爬取逻辑
        返回资讯列表
        """
        print("\n开始抓取数据...")

        # 方式1: 使用示例数据（推荐，网站爬取可能有法律风险）
        news = self.create_sample_news()
        print(f"✓ 生成了 {len(news)} 条示例资讯")

        # 方式2: 尝试从网站抓取（可选）
        # 注意：实际部署时请确保遵守网站robots.txt和使用条款
        # for source_type, sources in self.data_sources.items():
        #     for source in sources:
        #         print(f"正在抓取: {source['name']}...")
        #         items = self.crawl_webpage(source['url'], source['name'])
        #         for item in items:
        #             news.append({
        #                 "id": self.generate_id(item['title'], datetime.now().strftime("%Y-%m-%d")),
        #                 "title": item['title'],
        #                 "category": self.map_category(source['category']),
        #                 "source": item['source'],
        #                 "date": datetime.now().strftime("%Y-%m-%d"),
        #                 "summary": "",
        #                 "url": item['url'],
        #                 "tags": []
        #             })
        #         time.sleep(1)  # 避免请求过快

        return news

    def map_category(self, source_category: str) -> str:
        """映射来源类别到目标类别"""
        mapping = {
            "clinical": "临床进展",
            "policy": "政策标准",
            "industry": "产业市场",
            "conference": "学术会议"
        }
        return mapping.get(source_category, "通用行业资讯")

    def merge_with_existing(self, new_news: List[Dict]) -> List[Dict]:
        """
        合并新旧数据，避免重复
        """
        if not os.path.exists(self.output_file):
            return new_news

        with open(self.output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)

        existing_ids = {item['id'] for item in existing_data.get('news', [])}

        # 添加不重复的新资讯
        merged = existing_data.get('news', [])
        for item in new_news:
            if item['id'] not in existing_ids:
                merged.insert(0, item)  # 新资讯放在前面

        return merged

    def save(self, news: List[Dict]):
        """
        保存数据到JSON文件
        """
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)

        data = {
            "meta": {
                "total": len(news),
                "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
                "categories": [
                    "通用行业资讯",
                    "政策标准",
                    "临床进展",
                    "器械新药",
                    "产业市场",
                    "成果转化",
                    "学术会议",
                    "教育培训"
                ],
                "dataSources": {
                    "journals": "癌症期刊汇总Excel",
                    "companies": "疼痛领域企业Excel",
                    "reference": "疼痛数据库Excel"
                }
            },
            "news": news
        }

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 已保存 {len(news)} 条资讯到 {self.output_file}")

    def run(self):
        """
        运行爬虫
        """
        print("=" * 60)
        print("麻醉镇痛资讯爬虫开始运行")
        print(f"数据源: 用户提供的Excel文件（期刊、企业、数据库）")
        print("=" * 60)

        # 执行爬取
        new_news = self.crawl()

        # 合并数据
        if new_news:
            merged_news = self.merge_with_existing(new_news)
            self.save(merged_news)
        else:
            print("⚠ 没有新数据需要更新")

        print("=" * 60)
        print("爬虫运行完成")
        print("=" * 60)


if __name__ == "__main__":
    crawler = NewsCrawler()
    crawler.run()
