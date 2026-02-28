export default function Home() {
  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">Dashboard Candidatures</h2>
      <div className="grid grid-cols-3 gap-6">
        <div className="p-6 rounded-xl bg-gray-900 border border-gray-800 shadow-xl">
          <h3 className="text-lg font-medium text-gray-400">Nouvelles Offres</h3>
          <p className="text-4xl font-bold mt-2">0</p>
        </div>
      </div>
    </div>
  )
}
