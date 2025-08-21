import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          fontFamily: "Inter, system-ui",
          padding: 0,
          margin: 0,
        }}
      >
        <header className="site-header">
          <div className="container header-inner">
            <div className="brand">Taxely</div>
            <nav className="nav">
              <a href="#what">What</a>
              <a href="#how">How</a>
              <a href="#run">Run</a>
            </nav>
          </div>
        </header>
        <main className="container" style={{ padding: 24, maxWidth: 960 }}>
          {children}
        </main>
        <footer className="site-footer">
          <div className="container" style={{ padding: 16, maxWidth: 960 }}>
            <div style={{ opacity: 0.8 }}>Hackathon demo. Not tax advice.</div>
          </div>
        </footer>
      </body>
    </html>
  );
}
