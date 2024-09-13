# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import datetime

import requests
from requests.auth import HTTPBasicAuth
from collections import defaultdict

# 统计时间范围参数： 本周开始时间 - 今天
today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start_time = today - datetime.timedelta(days=today.weekday())
end_time = datetime.datetime.now()
start_time_str, end_time_str = start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d')

# 统计人员参数
users = [
    'xiaochuan.wang@proaimltd.com',
    'xiaoming.tang@proaimltd.com',
    'zihan.hu@proaimltd.com',
    'tianrong.sun@proaimltd.com',
    'yiqing.xu@proaimltd.com',
    'yong.wang@proaimltd.com',
    'xiao.hu@proaimltd.com',
    'haotian.lu@proaimltd.com',
    'ziming.xing@proaimltd.com',
]

alias_config = {
    'xiaochuan.wang@proaimltd.com': '王晓川',
    'xiaoming.tang@proaimltd.com': '唐晓明',
    'zihan.hu@proaimltd.com': '胡子寒',
    'tianrong.sun@proaimltd.com': '孙天荣',
    'yiqing.xu@proaimltd.com': '徐益庆',
    'yong.wang@proaimltd.com': '王 勇',
    'xiao.hu@proaimltd.com': '胡 晓',
    'haotian.lu@proaimltd.com': '卢浩天',
    'ziming.xing@proaimltd.com': '邢子铭'
}

# 认证参数
auth = HTTPBasicAuth('xiaochuan.wang@proaimltd.com',
                     "ATATT3xFfGF03jE3UtfYAw32W9oHiA6X7mdVfVZhphQGFutx4eUa13QURt8U9F9__rA7XF27gfyKdeb4VfahcCE4vxzBQo0HKxKsgmDgfRVNIt8jCfgAF8LQolONMflBKqGGGRveRUDdVDFO8iLb-H0jPNEY9XJFEGPM6P2CjBOzb9KAhczxhRA=EDBA7BD4")


class TimeLog(object):
    """
    工时记录
    """
    user, email, log_time, log_start_time, time_spent_seconds, issue_id, comment = [None for _ in range(7)]

    def __str__(self):
        return f'工时填报记录 ==> {self.user} | {self.email} | {self.log_time} | {self.log_start_time} | {self.log_start_time} | {self.time_spent_seconds} | {self.issue_id} | {self.comment} '


class TimeLogStatistics(object):
    time_logs: list[TimeLog] = []

    def add(self, time_logs):
        self.time_logs.append(time_logs)

    def group_by_user(self) -> dict:
        result = defaultdict(int)
        for tl in self.time_logs:
            result[tl.user] += round(tl.time_spent_seconds / 3600, 1)

        result = dict(result)
        print(result)
        return result


class DingRobot(object):
    """
    钉钉机器人: https://open.dingtalk.com/document/orgapp/custom-robots-send-group-messages
    """

    def __init__(self, webhook_url):
        self.url = webhook_url

    def send(self, message):
        data = {
            # 链接消息
            "link": {
                "messageUrl": "1",
                "picUrl": "1",
                "text": "1",
                "title": "1"
            },
            # 文本消息
            "text": {
                "content": f'--- 本周工时统计 【{start_time_str}】:【{end_time_str}】 ---\n' + message
            },
            # markdown消息
            "markdown": {
                "text": f"{message}",
                "title": "本周工时统计"
            },
            "msgtype": "markdown",
            # actionCard消息
        }
        print(self.url)
        print(data)
        res = requests.post(self.url, json=data)
        print(res.status_code, res.text)


def fetch_worklogs():
    users_params = [f'"{u}"' for u in users]
    headers = {"Content-Type": "application/json"}
    params = {
        'jql': f'worklogAuthor in ({",".join(users_params)}) AND worklogDate >= "{start_time_str}" ',
        'maxResults': 1000
    }

    # params = {'jql': f'worklogAuthor in ({",".join(users_params)}) AND worklogDate >= "2024-08-12" '}

    # 查询issue清单
    url = "https://proaim.atlassian.net/rest/api/3/search"
    response = requests.get(url, headers=headers, params=params, auth=auth)
    data = response.json()
    # 提取issue key列表
    issues = [issue['key'] for issue in data['issues']]
    print('查询到以下issue有工时登记: ', issues)
    stats = TimeLogStatistics()
    for issue in issues:
        # 查询指定issue的工时记录数据
        t1, t2 = int(start_time.timestamp()) * 1000, int(end_time.timestamp()) * 1000
        # 检索指定issue下的worklog的api
        worklog_url = "https://proaim.atlassian.net/rest/api/3/issue/%s/worklog"
        response = requests.get(worklog_url % issue, headers=headers, auth=auth, params={
            'startedAfter': t1,
            'startedBefore': t2
        })

        worklogs = response.json()['worklogs']
        # 遍历当前issue所有记录的工时
        for w in worklogs:
            contents = []
            # 工时填报内容提取
            if 'comment' in w and 'content' in w['comment']:
                for c in w['comment']['content']:
                    txts = [t.get('text') for t in c["content"] if 'text' in t]
                    contents.extend(txts)

            # 人员过滤
            email = w['updateAuthor']['emailAddress']
            if email not in users:
                continue

            # 生成工时记录对象
            time_log = TimeLog()
            time_log.user = alias_config.get(email) or email  # w['updateAuthor']['displayName']
            time_log.email = email
            time_log.log_time = w['created'][:19].replace('T', ' ')
            time_log.log_start_time = w['started'][:19].replace('T', ' ')
            time_log.time_spent_seconds = w['timeSpentSeconds']
            time_log.issue_id = w['issueId']
            time_log.comment = ' '.join(contents)

            print(time_log)
            stats.add(time_log)
            stats.group_by_user()
    user_worklogs = stats.group_by_user()
    result = {v: user_worklogs.get(v) or 0 for k, v in alias_config.items()}
    print(result)
    return result


if __name__ == '__main__':
    result = fetch_worklogs()

    # result = {'王晓川': 27.0, '唐晓明': 23.3, '胡子寒': 5.6, '孙天荣': 24.0, '徐益庆': 24.0, '王勇': 0, '胡晓': 15.5,
    #           '卢浩天': 24.5, '邢子铭': 28.0}

    # 钉钉机器人webhook地址 -- 测试群
    # ding_robot_wehook = 'https://oapi.dingtalk.com/robot/send?access_token=35eed9c7faf86d0ad319edd76d860e894b32a69d9d69fe090e11132e179c09c9'

    # 钉钉机器人webhook地址 -- 后端群
    ding_robot_wehook = 'https://oapi.dingtalk.com/robot/send?access_token=96f8ba1b33ac60b23069d24e2a2aa9e928413cecea157cdf1cae755684651b75'

    # 发送钉钉通知
    items = sorted([[k, v] for k, v in result.items()], key=lambda _: _[1], reverse=True)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    wd = datetime.datetime.now().weekday()
    weekday = f'星期{["一", "二", "三", "四", "五", "六", "日"][wd]}'
    message = f'**本周工时统计** (截止到{now} {weekday})\n'
    message += '\n---\n'
    qualified_wh = (wd + 1) * 8 if wd < 5 else 40
    message += '\n'.join([f'- {t[0]} : **{t[1]:.1f}**小时 {"☹️" if t[1] < qualified_wh else ""}' for t in items]) + '\n'
    message += '\n---\n'
    message += '\n **请及时准确填报工时!**\n'
    message += '\n-> [使用TimeTracker进行填报](https://proaim.atlassian.net/plugins/servlet/ac/org.everit.jira.timetracker.plugin/timetracker-page?project.key=YLNH&project.id=10106)\n'
    message += '\n-> [点击查看详细信息](https://proaim.atlassian.net/plugins/servlet/ac/clockwork-free-cloud/clockwork-timesheet?project.key=YLNH&project.id=10106#!reportName=Clockwork%20Timesheet&scope%5BstartingAt%5D=LAST_7_DAYS_START&scope%5BendingAt%5D=LAST_7_DAYS_END&selectedBreakdowns%5B%5D=users&selectedBreakdowns%5B%5D=issues&selectedFilters%5Busers%5D%5B%5D=64213fbf6b29c052ab2ed07c&selectedFilters%5Busers%5D%5B%5D=64213fc0f1b529dfa98e4948&selectedFilters%5Busers%5D%5B%5D=712020%3A53fe21ba-f60d-4611-83d0-3849c1d737cd&selectedFilters%5Busers%5D%5B%5D=712020%3Aacf75da1-1cd6-4cd1-8b59-166d0e7667cf&selectedFilters%5Busers%5D%5B%5D=712020%3Ab28acc9d-0ce0-4c58-bc70-ef6f86e3ee74&selectedFilters%5Busers%5D%5B%5D=712020%3Af3464bd5-98bc-4db8-9709-f02f71e30f92&selectedFilters%5Busers%5D%5B%5D=712020%3Af760f985-e9b7-4b5c-87bf-defb5f63a519&period=PERIOD_DAY&additionalColumn=)'
    robot = DingRobot(ding_robot_wehook)
    robot.send(message)
