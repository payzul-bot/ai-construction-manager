export const metadata = {
  title: "AI Construction Platform",
  description: "Project Passport and Engine UI"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        style={{
          fontFamily: "Inter, system-ui, sans-serif",
          margin: 0,
          backgroundColor: "#f6f7fb",
          color: "#1b1f2a"
        }}
      >
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 24px 48px" }}>
          {children}
        </div>
      </body>
    </html>
  );
}
