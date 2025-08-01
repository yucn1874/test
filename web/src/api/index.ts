// 将 types.ts 中的类型重新导出
export * from './types';
import request from './request'
import type { Note, Group, User, ProductPrice } from './types'
import axios from 'axios'

export const login = (data: { username: string; password: string }) => {
  return request.post('/auth/login/', data)
}

export const getNotes = (params?: any) => {
  return request.get<Note[]>('/notes/', { params })
}

export const createNote = (data: Partial<Note>) => {
  return request.post<Note>('/notes/', data)
}

export const updateNote = (id: string, data: Partial<Note>) => {
  return request.patch<Note>(`/notes/${id}/`, data)
}

export const deleteNote = (id: string) => {
  return request.delete(`/notes/${id}/`)
}

export const getGroups = () => {
  return request.get<Group[]>('/groups/')
}

export const createGroup = (data: Partial<Group>) => {
  return request.post<Group>('/groups/', data)
}

export const updateGroup = (id: string, data: Partial<Group>) => {
  return request.patch<Group>(`/groups/${id}/`, data)
}

export const deleteGroup = (id: string) => {
  return request.delete(`/groups/${id}/`)
}

export const getNoteStats = (params?: { range?: string }) => {
  return request.get('/notes/stats/', { params })
}

export const getActiveUsers = () => {
  return request.get('/auth/stats/')
}

export const getNote = (id: string) => {
  return request.get<Note>(`/notes/${id}/`)
}

export const getUsers = () => {
  return request.get<User[]>('/auth/users/')
}

export const createUser = (data: Partial<User>) => {
  return request.post<User>('/auth/users/', data)
}

export const updateUser = (id: string, data: Partial<User>) => {
  return request.patch<User>(`/auth/users/${id}/`, data)
}

export const deleteUser = (id: string) => {
  return request.delete(`/auth/users/${id}/`)
}

export const getAuthGroups = () => {
  return request.get<Group[]>('/auth/groups/')
}

export const createAuthGroup = (data: Partial<Group>) => {
  return request.post<Group>('/auth/groups/', data)
}

export const updateAuthGroup = (id: string, data: Partial<Group>) => {
  return request.patch<Group>(`/auth/groups/${id}/`, data)
}

export const deleteAuthGroup = (id: string) => {
  return request.delete(`/auth/groups/${id}/`)
}

export function fetchDashboardData() {
  return axios.get('/api/data_dashboard/');
}

/**
 * 获取价格数据列表，可选按 category 筛选
 */
export function getProductPrices(params?: { category?: string }) {
  return request.get<ProductPrice[]>('/product-prices/', { params });
}

/**
 * 创建价格数据
 */
export function createProductPrice(data: ProductPrice) {
  return request.post<ProductPrice>('/product-prices/', data);
}

/**
 * 更新价格数据
 */
export function updateProductPrice(id: number, data: ProductPrice) {
  return request.put<ProductPrice>(`/product-prices/${id}/`, data);
}

/**
 * 删除价格数据
 */
export function deleteProductPrice(id: number) {
  return request.delete(`/product-prices/${id}/`);
}

export function getCityCategoryAnalysis(year: number) {
  return request.get('/city-category-analysis/', {
    params: { year }
  })
}

// 获取价格和销量分析数据
export function getPriceSalesAnalysis() {
  return request.get('/price-sales-analysis/')
}

export function fetchVarietyWordcloud() {
  return request.get('/wordcloud/variety/')
}

export function fetchAreaWordcloud() {
  return request.get('/wordcloud/area/')
}


export function fetchForecast(variety: string) {
  return request.get('/forecast/', {
    params: { variety }
  })
}

// 获取仪表盘统计数据
export function fetchDashboardSummary() {
  return request.get('/dashboard/summary/')
}