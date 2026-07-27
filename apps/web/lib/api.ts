function withApiPrefix(value: string): string {
  const base = value.trim().replace(/\/+$/, '');
  return base.endsWith('/api/v1') ? base : `${base}/api/v1`;
}

export function getServerApiBase(): string {
  const configured =
    process.env.INTERNAL_API_URL ||
    process.env.API_EXTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL;

  return withApiPrefix(configured || 'http://localhost:8000/api/v1');
}
