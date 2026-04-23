import { useCallback, useRef, useState } from 'react'
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api'
import styles from './MapView.module.css'

const MAP_STYLES = [
  { elementType: 'geometry', stylers: [{ color: '#1a1a1a' }] },
  { elementType: 'labels.text.stroke', stylers: [{ color: '#1a1a1a' }] },
  { elementType: 'labels.text.fill', stylers: [{ color: '#a09890' }] },
  { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#2a2a2a' }] },
  { featureType: 'road', elementType: 'geometry.stroke', stylers: [{ color: '#212121' }] },
  { featureType: 'road', elementType: 'labels.text.fill', stylers: [{ color: '#9ca5b3' }] },
  { featureType: 'road.highway', elementType: 'geometry', stylers: [{ color: '#3a3a3a' }] },
  { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#17263c' }] },
  { featureType: 'poi', elementType: 'geometry', stylers: [{ color: '#242f3e' }] },
  { featureType: 'poi.park', elementType: 'geometry', stylers: [{ color: '#263c3f' }] },
]

const CONTAINER_STYLE = { width: '100%', height: '100%' }

export default function MapView({ center, pins }) {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
  const [selected, setSelected] = useState(null)

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: apiKey,
  })

  if (loadError) return (
    <div className={styles.fallback}>
      <p>지도를 불러오지 못했습니다.</p>
      <p className={styles.hint}>VITE_GOOGLE_MAPS_API_KEY를 .env에 설정해주세요.</p>
    </div>
  )

  if (!isLoaded) return <div className={styles.fallback}>지도 로딩 중...</div>

  return (
    <div className={styles.wrap}>
      <GoogleMap
        mapContainerStyle={CONTAINER_STYLE}
        center={center}
        zoom={15}
        options={{
          styles: MAP_STYLES,
          disableDefaultUI: false,
          zoomControl: true,
          mapTypeControl: false,
          streetViewControl: false,
          fullscreenControl: false,
        }}
      >
        {pins.map((pin, i) => (
          <Marker
            key={i}
            position={{ lat: parseFloat(pin.latitude), lng: parseFloat(pin.longitude) }}
            title={pin.name}
            icon={{
              path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z',
              fillColor: '#FF6B35',
              fillOpacity: 1,
              strokeColor: '#fff',
              strokeWeight: 1.5,
              scale: 1.6,
              anchor: { x: 12, y: 22 },
            }}
            onClick={() => setSelected(pin)}
          />
        ))}

        {selected && (
          <InfoWindow
            position={{ lat: parseFloat(selected.latitude), lng: parseFloat(selected.longitude) }}
            onCloseClick={() => setSelected(null)}
          >
            <div className={styles.infoWindow}>
              <strong>{selected.name}</strong>
              <span>{selected.address}</span>
              {selected.rating > 0 && <span>⭐ {selected.rating}</span>}
            </div>
          </InfoWindow>
        )}
      </GoogleMap>

      {pins.length > 0 && (
        <div className={styles.pinList}>
          {pins.map((pin, i) => (
            <button
              key={i}
              className={styles.pinItem}
              onClick={() => setSelected(pin)}
            >
              <span className={styles.pinNum}>{i + 1}</span>
              <span className={styles.pinName}>{pin.name}</span>
              {pin.rating > 0 && <span className={styles.pinRating}>⭐ {pin.rating}</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
