import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register } from '../api/client'
import styles from './AuthPage.module.css'

export default function RegisterPage() {
  const nav = useNavigate()
  const [form, setForm] = useState({ email: '', nickname: '', password1: '', password2: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password1 !== form.password2) { setError('비밀번호가 일치하지 않습니다.'); return }
    setLoading(true)
    try {
      await register(form)
      nav('/login')
    } catch (err) {
      setError(err.response?.data?.detail || '회원가입에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.card}>
        <h1 className={styles.logo}>MindFit</h1>
        <p className={styles.sub}>계정을 만들어보세요</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          {[
            { key: 'email',     label: '이메일',      type: 'email',    placeholder: 'example@email.com' },
            { key: 'nickname',  label: '닉네임',      type: 'text',     placeholder: '닉네임' },
            { key: 'password1', label: '비밀번호',    type: 'password', placeholder: '••••••••' },
            { key: 'password2', label: '비밀번호 확인', type: 'password', placeholder: '••••••••' },
          ].map(({ key, label, type, placeholder }) => (
            <div key={key}>
              <label className={styles.label}>{label}</label>
              <input
                className={styles.input}
                type={type}
                placeholder={placeholder}
                value={form[key]}
                onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))}
                required
              />
            </div>
          ))}

          {error && <p className={styles.error}>{error}</p>}
          <button className={styles.btn} type="submit" disabled={loading}>
            {loading ? '처리 중...' : '회원가입'}
          </button>
        </form>

        <p className={styles.footer}>
          이미 계정이 있으신가요?{' '}
          <Link to="/login" className={styles.link}>로그인</Link>
        </p>
      </div>
    </div>
  )
}
