export const statusText = {
  0: '已取消',
  1: '待支付',
  2: '已支付',
  3: '已完成',
}

export const statusType = {
  0: 'info',
  1: 'warning',
  2: 'primary',
  3: 'success',
}

export function money(value) {
  return `¥${Number(value || 0).toFixed(2)}`
}

export function pageRecords(page) {
  return page?.records || page?.list || []
}
