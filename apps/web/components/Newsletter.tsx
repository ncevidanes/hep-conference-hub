'use client';

import { useState } from 'react';

export default function Newsletter() {
  const [email, setEmail] = useState('');
  const [msg, setMsg] = useState('');

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setMsg('Enviando...');

    try {
      const response = await fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          areas: ['high-energy-physics', 'CERN', 'particle-collisions'],
          frequency: 'weekly',
        }),
      });

      setMsg(response.ok ? 'Assinatura registrada.' : 'Não foi possível registrar.');
    } catch {
      setMsg('Não foi possível registrar.');
    }
  }

  return (
    <section className="newsletter">
      <h2>Radar semanal de HEP</h2>
      <p>
        Submissões abertas, prazos prorrogados e eventos do CERN, LHC, ATLAS,
        CMS, ALICE e LHCb.
      </p>
      <form onSubmit={submit}>
        <input
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          type="email"
          required
          placeholder="seu@email.com"
        />
        <button className="button">Assinar</button>
      </form>
      {msg && <p>{msg}</p>}
    </section>
  );
}
