import { io } from 'socket.io-client'

const URL = `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}`

export const socket = io(URL)