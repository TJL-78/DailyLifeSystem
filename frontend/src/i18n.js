import { ref } from 'vue'

const currentLang = ref(localStorage.getItem('lang') || 'zh')

const I18N = {
  zh: {
    appTitle: '活动管理', dashboard: '仪表盘', allActivities: '全部活动',
    calendarView: '日历视图', habitTrack: '习惯追踪', journalNav: '每日日志', statistics: '统计分析',
    categoryLabel: '分类', manageCategories: '管理分类', settingsNav: '个人设置',
    logout: '退出登录', settings: '个人设置', langSwitch: '语言切换',
    avatar: '头像设置', chooseAvatar: '选择图片', uploadAvatar: '上传头像',
    avatarHint: '支持 JPG/PNG 格式，不超过 2MB',
    profile: '个人资料', displayName: '显示名称', emailPlaceholder: '邮箱',
    phonePlaceholder: '手机号（如：13800138000）', save: '保存',
    changePassword: '修改密码', oldPw: '旧密码', newPw: '新密码（至少6位）', changePwBtn: '修改',
    dashTitle: '仪表盘', totalActs: '总活动', pending: '待办', inProgress: '进行中',
    completed: '已完成', completionRate: '完成率', todayTodo: '今日待办',
    recentActs: '近期活动', noTodayActs: '今日暂无安排', noActs: '暂无活动',
    actTitle: '全部活动', searchPlaceholder: '搜索活动（标题、描述、标签）...',
    search: '搜索', clear: '清除', addActivity: '添加活动',
    titlePlaceholder: '活动标题 *', low: '低', medium: '中', high: '高', urgent: '紧急',
    noCategory: '无分类', descPlaceholder: '描述（可选）', durationPlaceholder: '时长(分)',
    noRepeat: '不重复', daily: '每天', weekly: '每周', monthly: '每月',
    tagsPlaceholder: '标签（逗号分隔，如：重要,会议）', add: '添加',
    allStatus: '全部状态', allPriority: '全部优先级', allCategory: '全部分类',
    catManage: '分类管理', catNamePlaceholder: '分类名称 *', iconPlaceholder: '图标(emoji)',
    noCats: '暂无分类', confirmDeleteCat: '确定删除此分类？',
    habitsTitle: '习惯追踪', addHabit: '添加习惯', habitNamePlaceholder: '习惯名称 *',
    habitDescPlaceholder: '描述（可选）', noHabits: '暂无习惯，添加一个开始追踪吧',
    confirmDeleteHabit: '确定删除此习惯及所有记录？',
    statsTitle: '统计分析', totalCompleted: '已完成', totalTime: '总投入时间', tasks: '个任务',
    catDistribution: '分类分布', weeklyTrend: '每周趋势（近4周）',
    exportJSON: '导出 JSON', exportCSV: '导出 CSV', noData: '暂无数据',
    newAdded: '新增', completedLabel: '完成', weekLabel: '周',
    calTitle: '日历视图', prevYear: '◀◀', prevMonth: '◀', nextMonth: '▶', nextYear: '▶▶', calToday: '今天',
    dayDetail: '的活动', noDayActs: '当天无活动', noMatch: '未找到匹配的活动',
    start: '开始', cancel: '取消', delete: '删除', confirmDelete: '确定删除？',
    subtask: '子任务', addSubtaskPlaceholder: '添加子任务...',
    daysAgo30: '30天前', today: '今天',
    profileUpdated: '更新成功', phoneInvalid: '手机号格式不正确',
    pwChanged: '密码修改成功', avatarUpdated: '头像更新成功',
    unclassified: '未分类',
    catTimeTitle: '分类执行时间分析',
    totalTime2: '总计', minutes: '分钟', proportion: '占比',
    noTimeData: '暂无执行时间数据（请为活动设置时长）',
    journalTitle: '每日日志', writeJournal: '撰写日志', journalDate: '日期',
    weather: '天气', mood: '心情', journalContent: '日志内容',
    contentPlaceholder: '记录今天的点滴...', saveJournal: '保存日志',
    weatherPlaceholder: '输入天气，如：晴、多云、小雨...',
    moodPlaceholder: '输入心情，如：开心、平静、疲惫...',
    filterWeather: '筛选天气', filterMood: '筛选心情',
    templateSaveFailed: '保存模板失败',
    journalHistory: '历史日志', noJournals: '暂无日志记录',
    journalSaved: '日志已保存', confirmDeleteJournal: '确定删除这篇日志？',
    weatherSunny: '☀️ 晴', weatherCloudy: '⛅ 多云', weatherOvercast: '☁️ 阴',
    weatherRainy: '🌧️ 雨', weatherSnowy: '❄️ 雪', weatherWindy: '💨 大风',
    moodHappy: '😊 开心', moodCalm: '😌 平静', moodSad: '😢 难过',
    moodAngry: '😤 生气', moodTired: '😴 疲惫', moodExcited: '🤩 兴奋',
    clickUploadImages: '点击上传图片（最多9张）',
    commentPlaceholder: '写评论...', sendComment: '发送',
    clearJournal: '一键清空', confirmClearJournal: '确定清空所有内容、天气、心情和图片吗？',
    // Pomodoro
    pomodoroTitle: '番茄钟', focusTimer: '专注计时', startTimer: '开始',
    pauseTimer: '暂停', resetTimer: '重置', sessionComplete: '专注完成！',
    todayFocus: '今日专注', sessions: '次', totalMinutes: '总分钟',
    selectActivity: '关联活动（可选）', noActivity: '不关联', pomodoroHistory: '今日记录',
    // Goals
    goalsTitle: '目标管理', goalsNav: '目标', addGoal: '添加目标',
    goalTitle: '目标标题', targetValue: '目标值', goalUnit: '单位',
    goalPeriod: '周期', goalWeekly: '每周', goalMonthly: '每月', goalYearly: '每年',
    currentProgress: '当前进度', addProgress: '添加进度', progressValue: '进度值',
    noGoals: '暂无目标', confirmDeleteGoal: '确定删除此目标？',
    // Heatmap
    heatmapTitle: '年度热力图', heatmapNav: '热力图', monthlyReport: '月度报告',
    activitiesCount: '活动数', lessActive: '少', moreActive: '多',
    // Templates
    templatesTitle: '活动模板', templatesNav: '模板', useTemplate: '使用模板',
    saveAsTemplate: '存为模板', noTemplates: '暂无模板', confirmDeleteTemplate: '确定删除此模板？',
    templateSaved: '模板已保存', templateUsed: '已从模板创建活动',
    // Tags
    tagsTitle: '标签管理', tagsNav: '标签', tagUsageCount: '使用次数',
    renameTag: '重命名', tagColor: '颜色', noTags: '暂无标签',
    confirmDeleteTag: '确定删除此标签？将从所有活动中移除',
    // Notifications
    enableNotifications: '启用通知', notificationsEnabled: '通知已启用',
    notificationsDenied: '通知权限被拒绝',
    // Dark mode
    darkMode: '深色模式',
    // Kanban
    kanbanTitle: '看板视图', kanbanNav: '看板',
    // Backup
    exportData: '导出全部数据', importData: '导入数据',
    dataExported: '数据已导出', dataImported: '数据已导入',
    // Sharing
    shareActivity: '分享', shareUsername: '用户名', sharePermission: '权限',
    shareRead: '只读', shareEdit: '可编辑', shared: '已分享',
    // Journal enhancements
    searchJournal: '搜索日志...', filterMonth: '筛选月份', allMonths: '全部月份',
    allWeather: '全部天气', allMood: '全部心情',
    // Dashboard enhancements
    todayOverview: '今日概览', quickActions: '快捷操作',
    addActivityQuick: '添加活动', startPomodoroQuick: '开始番茄钟', writeJournalQuick: '写日志',
    activeHabits: '活跃习惯', checkedToday: '今日已打卡', activeGoals: '进行中目标',
    greeting: '你好',
    // Recurring
    recurringBadge: '重复', recurringGenerated: '已生成重复任务', noRecurring: '无重复任务',
    // Pomodoro enhancements
    customDuration: '自定义', breakTime: '休息中', breakComplete: '休息结束！',
    startBreak: '开始休息', skipBreak: '跳过休息',
    soundOption: '提示音', soundShort: '短提示音', soundLong: '长提示音', soundMelody: '旋律提示音',
    // Timeline
    timelineNav: '时间线', timelineTitle: '时间线视图', prevDay: '前一天', nextDay: '后一天',
    unscheduled: '未安排时间', currentTime: '当前时间', noTimelineActs: '当天无活动',
    // Report
    reportNav: '报告', reportTitle: '智能报告', dailyReport: '日报', weeklyReport: '周报',
    generateReport: '生成报告', generating: '生成中...', copyReport: '复制到剪贴板',
    exportMarkdown: '导出 Markdown', reportCopied: '已复制到剪贴板', noReportData: '暂无数据生成报告',
    recommendations: '建议', activityOverview: '活动概览', timeAnalysis: '时间分析',
    habitSummary: '习惯总结', journalSummary: '日志概况', goalProgress: '目标进度',
  },
  en: {
    appTitle: 'Activity Manager', dashboard: 'Dashboard', allActivities: 'All Activities',
    calendarView: 'Calendar', habitTrack: 'Habits', journalNav: 'Journal', statistics: 'Statistics',
    categoryLabel: 'Categories', manageCategories: 'Manage Categories', settingsNav: 'Settings',
    logout: 'Logout', settings: 'Settings', langSwitch: 'Language',
    avatar: 'Avatar', chooseAvatar: 'Choose Image', uploadAvatar: 'Upload',
    avatarHint: 'JPG/PNG, max 2MB',
    profile: 'Profile', displayName: 'Display Name', emailPlaceholder: 'Email',
    phonePlaceholder: 'Phone number', save: 'Save',
    changePassword: 'Change Password', oldPw: 'Old password', newPw: 'New password (min 6)', changePwBtn: 'Change',
    dashTitle: 'Dashboard', totalActs: 'Total', pending: 'Pending', inProgress: 'In Progress',
    completed: 'Completed', completionRate: 'Rate', todayTodo: "Today's Tasks",
    recentActs: 'Recent Activities', noTodayActs: 'Nothing scheduled today', noActs: 'No activities',
    actTitle: 'All Activities', searchPlaceholder: 'Search activities...',
    search: 'Search', clear: 'Clear', addActivity: 'Add Activity',
    titlePlaceholder: 'Title *', low: 'Low', medium: 'Medium', high: 'High', urgent: 'Urgent',
    noCategory: 'No category', descPlaceholder: 'Description (optional)', durationPlaceholder: 'Duration(min)',
    noRepeat: 'No repeat', daily: 'Daily', weekly: 'Weekly', monthly: 'Monthly',
    tagsPlaceholder: 'Tags (comma separated)', add: 'Add',
    allStatus: 'All status', allPriority: 'All priority', allCategory: 'All categories',
    catManage: 'Category Management', catNamePlaceholder: 'Category name *', iconPlaceholder: 'Icon(emoji)',
    noCats: 'No categories', confirmDeleteCat: 'Delete this category?',
    habitsTitle: 'Habit Tracking', addHabit: 'Add Habit', habitNamePlaceholder: 'Habit name *',
    habitDescPlaceholder: 'Description (optional)', noHabits: 'No habits yet',
    confirmDeleteHabit: 'Delete this habit and all records?',
    statsTitle: 'Statistics', totalCompleted: 'Completed', totalTime: 'Total Time', tasks: 'tasks',
    catDistribution: 'Category Distribution', weeklyTrend: 'Weekly Trend (4 weeks)',
    exportJSON: 'Export JSON', exportCSV: 'Export CSV', noData: 'No data',
    newAdded: 'New', completedLabel: 'Done', weekLabel: 'week',
    calTitle: 'Calendar', prevYear: '◀◀', prevMonth: '◀', nextMonth: '▶', nextYear: '▶▶', calToday: 'Today',
    dayDetail: ' activities', noDayActs: 'No activities this day', noMatch: 'No matching activities',
    start: 'Start', cancel: 'Cancel', delete: 'Delete', confirmDelete: 'Confirm delete?',
    subtask: 'Subtask', addSubtaskPlaceholder: 'Add subtask...',
    daysAgo30: '30 days ago', today: 'Today',
    profileUpdated: 'Updated', phoneInvalid: 'Invalid phone number',
    pwChanged: 'Password changed', avatarUpdated: 'Avatar updated',
    unclassified: 'Uncategorized',
    catTimeTitle: 'Category Time Analysis',
    totalTime2: 'Total', minutes: 'min', proportion: 'Share',
    noTimeData: 'No time data',
    journalTitle: 'Daily Journal', writeJournal: 'Write Journal', journalDate: 'Date',
    weather: 'Weather', mood: 'Mood', journalContent: 'Content',
    contentPlaceholder: 'Record your day...', saveJournal: 'Save',
    weatherPlaceholder: 'e.g. Sunny, Cloudy, Rainy...',
    moodPlaceholder: 'e.g. Happy, Calm, Tired...',
    filterWeather: 'Filter weather', filterMood: 'Filter mood',
    templateSaveFailed: 'Failed to save template',
    journalHistory: 'Journal History', noJournals: 'No journal entries yet',
    journalSaved: 'Journal saved', confirmDeleteJournal: 'Delete this journal?',
    weatherSunny: '☀️ Sunny', weatherCloudy: '⛅ Cloudy', weatherOvercast: '☁️ Overcast',
    weatherRainy: '🌧️ Rainy', weatherSnowy: '❄️ Snowy', weatherWindy: '💨 Windy',
    moodHappy: '😊 Happy', moodCalm: '😌 Calm', moodSad: '😢 Sad',
    moodAngry: '😤 Angry', moodTired: '😴 Tired', moodExcited: '🤩 Excited',
    clickUploadImages: 'Click to upload images (max 9)',
    commentPlaceholder: 'Write a comment...', sendComment: 'Send',
    clearJournal: 'Clear All', confirmClearJournal: 'Clear all content, weather, mood and images?',
    // Pomodoro
    pomodoroTitle: 'Pomodoro', focusTimer: 'Focus Timer', startTimer: 'Start',
    pauseTimer: 'Pause', resetTimer: 'Reset', sessionComplete: 'Session complete!',
    todayFocus: "Today's Focus", sessions: 'sessions', totalMinutes: 'total min',
    selectActivity: 'Link activity (optional)', noActivity: 'None', pomodoroHistory: "Today's Sessions",
    // Goals
    goalsTitle: 'Goals', goalsNav: 'Goals', addGoal: 'Add Goal',
    goalTitle: 'Goal title', targetValue: 'Target value', goalUnit: 'Unit',
    goalPeriod: 'Period', goalWeekly: 'Weekly', goalMonthly: 'Monthly', goalYearly: 'Yearly',
    currentProgress: 'Current Progress', addProgress: 'Add Progress', progressValue: 'Value',
    noGoals: 'No goals yet', confirmDeleteGoal: 'Delete this goal?',
    // Heatmap
    heatmapTitle: 'Annual Heatmap', heatmapNav: 'Heatmap', monthlyReport: 'Monthly Report',
    activitiesCount: 'Activities', lessActive: 'Less', moreActive: 'More',
    // Templates
    templatesTitle: 'Activity Templates', templatesNav: 'Templates', useTemplate: 'Use Template',
    saveAsTemplate: 'Save as Template', noTemplates: 'No templates yet', confirmDeleteTemplate: 'Delete this template?',
    templateSaved: 'Template saved', templateUsed: 'Activity created from template',
    // Tags
    tagsTitle: 'Tag Management', tagsNav: 'Tags', tagUsageCount: 'Usage count',
    renameTag: 'Rename', tagColor: 'Color', noTags: 'No tags yet',
    confirmDeleteTag: 'Delete this tag? It will be removed from all activities',
    // Notifications
    enableNotifications: 'Enable Notifications', notificationsEnabled: 'Notifications enabled',
    notificationsDenied: 'Notification permission denied',
    // Dark mode
    darkMode: 'Dark Mode',
    // Kanban
    kanbanTitle: 'Kanban Board', kanbanNav: 'Kanban',
    // Backup
    exportData: 'Export All Data', importData: 'Import Data',
    dataExported: 'Data exported', dataImported: 'Data imported',
    // Sharing
    shareActivity: 'Share', shareUsername: 'Username', sharePermission: 'Permission',
    shareRead: 'Read only', shareEdit: 'Can edit', shared: 'Shared',
    // Journal enhancements
    searchJournal: 'Search journals...', filterMonth: 'Filter month', allMonths: 'All months',
    allWeather: 'All weather', allMood: 'All moods',
    // Dashboard enhancements
    todayOverview: "Today's Overview", quickActions: 'Quick Actions',
    addActivityQuick: 'Add Activity', startPomodoroQuick: 'Start Pomodoro', writeJournalQuick: 'Write Journal',
    activeHabits: 'Active Habits', checkedToday: 'Checked', activeGoals: 'Active Goals',
    greeting: 'Hello',
    // Recurring
    recurringBadge: 'Recurring', recurringGenerated: 'Recurring tasks generated', noRecurring: 'No recurring tasks',
    // Pomodoro enhancements
    customDuration: 'Custom', breakTime: 'Break Time', breakComplete: 'Break complete!',
    startBreak: 'Start Break', skipBreak: 'Skip Break',
    soundOption: 'Sound', soundShort: 'Short beep', soundLong: 'Long beep', soundMelody: 'Melody',
    // Timeline
    timelineNav: 'Timeline', timelineTitle: 'Timeline View', prevDay: 'Prev Day', nextDay: 'Next Day',
    unscheduled: 'Unscheduled', currentTime: 'Now', noTimelineActs: 'No activities today',
    // Report
    reportNav: 'Report', reportTitle: 'Smart Report', dailyReport: 'Daily', weeklyReport: 'Weekly',
    generateReport: 'Generate Report', generating: 'Generating...', copyReport: 'Copy to Clipboard',
    exportMarkdown: 'Export Markdown', reportCopied: 'Copied to clipboard', noReportData: 'No data for report',
    recommendations: 'Recommendations', activityOverview: 'Activity Overview', timeAnalysis: 'Time Analysis',
    habitSummary: 'Habit Summary', journalSummary: 'Journal Summary', goalProgress: 'Goal Progress',
  }
}

export function useI18n() {
  function t(key) {
    return (I18N[currentLang.value] || I18N.zh)[key] || key
  }
  function switchLang(lang) {
    currentLang.value = lang
    localStorage.setItem('lang', lang)
  }
  return { t, currentLang, switchLang }
}
