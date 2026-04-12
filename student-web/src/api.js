import axios from 'axios'

const http = axios.create({ baseURL: '/api', timeout: 10000 })

http.interceptors.request.use(cfg => {
  const token = localStorage.getItem('student_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

http.interceptors.response.use(
  r => r.data,
  err => {
    const msg = err.response?.data?.message || err.message
    if (err.response?.status === 401) {
      localStorage.removeItem('student_token')
      location.href = '/login'
    }
    return Promise.reject(new Error(msg))
  }
)

export default http
