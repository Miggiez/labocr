import React, { useState, useEffect } from "react"
import io, { Socket } from "socket.io-client"
import {
	LineChart,
	Line,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
	Legend,
	ResponsiveContainer,
} from "recharts"

interface RecordedData {
	value: string
}

export const Sockets = () => {
	const [image, setImage] = useState<string>("none")
	const [socketInstance, setSocketInstance] = useState<Socket>()
	const [isConnected, setIsConnected] = useState<boolean>(false)
	const [val, setVal] = useState<string>("")
	const [isRec, setIsRec] = useState<boolean>(false)
	const [recData, setRecData] = useState<RecordedData[]>([])
	const [isOpen, setIsOpen] = useState<boolean>(false)

	useEffect(() => {
		const socket = io("http://localhost:9928/")
		setSocketInstance(socket)
		socket.on("connect", () => {
			console.log("Connected from server")
			setIsConnected(true)
		})
		socket.on("disconnect", () => {
			console.log("Disconnected from server")
			setIsConnected(false)
			setIsOpen(false)
			setIsRec(false)
		})
		socket.on("switch", (data) => {
			setIsOpen(data.data)
		})
		socket.on("data", (data) => {
			setImage(data.message)
			setVal(data.val)
		})
		return () => {
			socket.close()
		}
	}, [])

	useEffect(() => {
		let intervalId: number
		if (isRec == true) {
			intervalId = setInterval(() => {
				if (val != "") {
					let newob = {
						value: val,
					}
					console.log(intervalId)
					setRecData((data) => [...data, newob])
				}
			}, 1000)
		}

		return () => clearInterval(intervalId)
	}, [isRec, val])

	const handleStart = (e: React.MouseEvent<HTMLButtonElement>) => {
		e.preventDefault()
		if (isConnected == true && isOpen == false) {
			socketInstance?.emit("switch", true)
			socketInstance?.emit("data")
		}
	}

	const handleStop = (e: React.MouseEvent<HTMLButtonElement>) => {
		e.preventDefault()
		if (isConnected == true && isOpen == true) {
			socketInstance?.emit("switch", false)
			setImage("none")
			setIsRec(false)
		}
	}

	const handleRecord = (e: React.MouseEvent<HTMLButtonElement>) => {
		e.preventDefault()
		if (isConnected == true && isOpen == true) {
			setIsRec(!isRec)
		}
	}

	const handleRefresh = (e: React.MouseEvent<HTMLButtonElement>) => {
		e.preventDefault()
		setRecData([])
	}

	return (
		<div className="flex flex-col w-full h-screen">
			<h1 className="flex justify-center text-3xl items-center bg-black text-white p-4">
				<span className="font-bold">Camera:</span>
				<span className="text-2xl pl-3">
					{isConnected ? (
						<span className="text-green-400">connected</span>
					) : (
						<span className="text-red-400">disconnected</span>
					)}
				</span>
			</h1>
			<p className="text-2xl font-bold flex justify-center">Value: {val}</p>
			<div className="grid grid-cols-3 gap-4 h-full w-full">
				<div className="bg-green-200 col-span-2 flex justify-around p-3 items-center">
					{isOpen ? (
						<img
							className="rounded-md h-[340px] w-[420px] "
							src={image}
							height="340"
							width="420"
						/>
					) : (
						<div className="h-[340px] w-[420px] bg-black rounded-md"></div>
					)}
					<div className="flex flex-col justify-around h-full">
						<button
							className="bg-white drop-shadow-lg font-bold text-xl px-10 py-4 rounded-lg"
							onClick={handleStart}
						>
							Start
						</button>
						<button
							className="bg-white drop-shadow-lg font-bold text-xl px-10 py-4 rounded-lg"
							onClick={handleStop}
						>
							Stop
						</button>
						<button
							className={
								isRec
									? "font-bold text-xl px-10 py-4 rounded-lg text-black bg-red-600 shadow-inner"
									: "font-bold text-xl px-10 py-4 rounded-lg text-black bg-green-600 drop-shadow-xl shadow-xl"
							}
							onClick={handleRecord}
						>
							Record
						</button>
					</div>
				</div>
				<div className="bg-red-200 flex flex-col items-center p-3 h-full ">
					<div className="w-full flex justify-center items-center mb-2">
						<button
							className="relative right-20 bg-white py-1 px-2 rounded-md drop-shadow-md"
							onClick={handleRefresh}
						>
							Refresh
						</button>
						<h1 className="font-bold text-xl">Recorded values</h1>
					</div>

					<div className="w-full text-black scroll-auto overflow-x-hidden overflow-y-scroll h-[400px]">
						{recData.map((data, i) => (
							<div
								className="bg-white w-full p-2 m-2 rounded flex justify-center"
								key={i}
							>
								<p>
									<span>data#: {i}</span>
									<span className="pl-3">val: {data.value}</span>
								</p>
							</div>
						))}
					</div>
				</div>
			</div>
			<div className="bg-blue-200 w-full h-full mt-4 pt-2">
				<ResponsiveContainer width="100%" height="100%">
					<LineChart
						width={500}
						height={300}
						data={recData}
						margin={{
							top: 5,
							right: 30,
							left: 20,
							bottom: 5,
						}}
					>
						<CartesianGrid strokeDasharray="3 3" />
						<XAxis />
						<YAxis />
						<Tooltip />
						<Legend />
						{/* <Line
							type="monotone"
							dataKey="pv"
							stroke="#8884d8"
							activeDot={{ r: 8 }}
						/> */}
						<Line
							type="monotone"
							dataKey="value"
							stroke="#000000"
							activeDot={{ r: 8 }}
						/>
					</LineChart>
				</ResponsiveContainer>
			</div>
		</div>
	)
}

export default Socket
