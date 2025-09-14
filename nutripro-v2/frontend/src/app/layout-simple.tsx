import './globals.css';

export const metadata = {
  title: 'NutriPro V2',
  description: 'Plataforma de gestão nutricional modernizada',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}