import React, { useState, useEffect } from "react"
import io, { Socket } from "socket.io-client"

export const Sockets = () => {
	const [image, setImage] = useState<string>("none")
	const [socketInstance, setSocketInstance] = useState<Socket>()
	const [isConntected, setIsConnected] = useState<string>("Is disconnected")
	const [isOpen, setIsOpen] = useState<boolean>(false)
	useEffect(() => {
		const socket = io("http://localhost:9928/")
		setSocketInstance(socket)
		socket.on("connect", () => {
			console.log("Connected from server")
			setIsConnected("Is Connected")
		})
		socket.on("disconnect", () => {
			console.log("Disconnected from server")
			setIsConnected("Is Disconnected")
			setIsOpen(false)
		})
		socket.on("switch", (data) => {
			setIsOpen(data.data)
		})
		socket.on("data", (data) => {
			setImage(data.message)
		})
		return () => {
			socket.close()
		}
	}, [])
	const handleStart = (e: React.MouseEvent<HTMLButtonElement>) => {
		e.preventDefault()
		socketInstance?.emit("switch", true)
		socketInstance?.emit("data")
	}
	const handleStop = (e: React.MouseEvent<HTMLButtonElement>) => {
		e.preventDefault()
		socketInstance?.emit("switch", false)
		setImage("none")
	}
	return (
		<div>
			<h1>Camera</h1>
			<p>Server is: {isConntected}</p>
			<button onClick={handleStart}>start</button>
			<button onClick={handleStop}>stop</button>
			{isOpen ? <img src={image} /> : ""}
		</div>
	)
}

export default Socket
