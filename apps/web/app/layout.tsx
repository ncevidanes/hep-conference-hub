import './globals.css';
export const metadata={title:'HEP Conference Hub',description:'Radar de congressos, simpósios e chamadas de trabalhos em física de altas energias.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="pt-BR"><body><div className="wrap"><nav className="nav"><a className="brand" href="/">HEP Conference Hub</a><div><a href="/admin">Painel</a></div></nav>{children}</div></body></html>}
