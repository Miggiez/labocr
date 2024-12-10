// import { useEffect } from "react"

import "./App.css"
// import { Command } from "@tauri-apps/plugin-shell"
import { Sockets } from "./components/Socket"

function App() {
	// const streaming = async () => {
	// 	const command = Command.sidecar("bin/python/stream")
	// 	const output = await command.execute()
	// 	console.log(output)
	// }

	// useEffect(() => {
	// 	streaming()
	// }, [])

	return (
		// <div>
		// 	<div>Camera </div>
		// 	<img src={image} />
		// </div>
		<Sockets />
	)
}

export default App
