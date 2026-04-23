import { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api/client'
import styles from './ChatWindow.module.css'

export default function ChatWindow({ onNewPins }) {
  const [messages, setMessages] = useState([
    { role: 'bot', text: '안녕하세요! 경기대 근처 맛집을 추천해드릴게요 😋\n"매운 음식 추천해줘" 처럼 말씀해보세요!' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || loading) return

    setMessages(prev => [...prev, { role: 'user', text }])
    setInput('')
    setLoading(true)

    try {
      const res = await sendMessage(text)
      const { response, restaurants } = res.data

      setMessages(prev => [...prev, { role: 'bot', text: response }])

      if (restaurants && restaurants.length > 0) {
        onNewPins(restaurants)
      }
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: '오류가 발생했어요. 다시 시도해주세요.' }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.messages}>
        {messages.map((msg, i) => (
          <div key={i} className={`${styles.msg} ${styles[msg.role]}`}>
            {msg.role === 'bot' && <span className={styles.avatar}>🍜</span>}
            <div className={styles.bubble}>
              {msg.text.split('\n').map((line, j) => (
                <span key={j}>{line}{j < msg.text.split('\n').length - 1 && <br />}</span>
              ))}
            </div>
          </div>
        ))}
        {loading && (
          <div className={`${styles.msg} ${styles.bot}`}>
            <span className={styles.avatar}>🍜</span>
            <div className={`${styles.bubble} ${styles.typing}`}>
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className={styles.inputRow}>
        <textarea
          className={styles.textarea}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="메시지를 입력하세요..."
          rows={1}
        />
        <button
          className={styles.sendBtn}
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          ↑
        </button>
      </div>
    </div>
  )
}
