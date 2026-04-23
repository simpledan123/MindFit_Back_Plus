import { useState, useEffect } from 'react'
import { getBookmarks, removeBookmark } from '../api/client'
import styles from './BookmarkList.module.css'

export default function BookmarkList({ onPinClick }) {
  const [bookmarks, setBookmarks] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchBookmarks = async () => {
    try {
      const res = await getBookmarks()
      setBookmarks(res.data)
    } catch {
      // 에러 무시
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchBookmarks() }, [])

  const handleRemove = async (e, id) => {
    e.stopPropagation()
    try {
      await removeBookmark(id)
      setBookmarks(prev => prev.filter(b => b.id !== id))
    } catch {
      alert('삭제에 실패했습니다.')
    }
  }

  if (loading) return <div className={styles.empty}>불러오는 중...</div>

  if (bookmarks.length === 0) return (
    <div className={styles.empty}>
      <p>북마크한 식당이 없어요.</p>
      <p className={styles.hint}>챗봇에게 추천을 받아보세요!</p>
    </div>
  )

  return (
    <div className={styles.wrap}>
      <p className={styles.count}>{bookmarks.length}개의 북마크</p>
      <ul className={styles.list}>
        {bookmarks.map(b => (
          <li key={b.id} className={styles.item} onClick={() => onPinClick(b)}>
            <div className={styles.info}>
              <span className={styles.name}>{b.name}</span>
              <span className={styles.address}>{b.address}</span>
              {b.rating > 0 && <span className={styles.rating}>⭐ {b.rating}</span>}
            </div>
            <button
              className={styles.removeBtn}
              onClick={(e) => handleRemove(e, b.id)}
              title="북마크 삭제"
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
