import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ChatWindow from '../components/ChatWindow'
import MapView from '../components/MapView'
import BookmarkList from '../components/BookmarkList'
import styles from './MainPage.module.css'

export default function MainPage() {
  const nav = useNavigate()
  const [pins, setPins] = useState([])          // 지도에 표시할 식당들
  const [tab, setTab] = useState('chat')         // 'chat' | 'bookmarks'
  const [mapCenter, setMapCenter] = useState({ lat: 37.2977, lng: 127.0435 }) // 경기대 기본 위치

  const handleLogout = () => {
    localStorage.removeItem('token')
    nav('/login')
  }

  // 챗봇 응답으로 식당 핀 업데이트
  const handleNewPins = (restaurants) => {
    if (!restaurants || restaurants.length === 0) return
    setPins(restaurants)
    setMapCenter({
      lat: parseFloat(restaurants[0].latitude),
      lng: parseFloat(restaurants[0].longitude),
    })
  }

  return (
    <div className={styles.layout}>
      {/* ── 사이드바 ── */}
      <aside className={styles.sidebar}>
        <div className={styles.sideTop}>
          <h1 className={styles.logo}>MindFit</h1>
          <nav className={styles.tabNav}>
            <button
              className={`${styles.tabBtn} ${tab === 'chat' ? styles.active : ''}`}
              onClick={() => setTab('chat')}
            >
              💬 챗봇
            </button>
            <button
              className={`${styles.tabBtn} ${tab === 'bookmarks' ? styles.active : ''}`}
              onClick={() => setTab('bookmarks')}
            >
              🔖 북마크
            </button>
          </nav>
        </div>

        <div className={styles.sideContent}>
          {tab === 'chat'
            ? <ChatWindow onNewPins={handleNewPins} />
            : <BookmarkList onPinClick={(r) => {
                setPins([r])
                setMapCenter({ lat: parseFloat(r.latitude), lng: parseFloat(r.longitude) })
              }} />
          }
        </div>

        <button className={styles.logoutBtn} onClick={handleLogout}>로그아웃</button>
      </aside>

      {/* ── 지도 ── */}
      <main className={styles.mapArea}>
        <MapView center={mapCenter} pins={pins} />
      </main>
    </div>
  )
}
