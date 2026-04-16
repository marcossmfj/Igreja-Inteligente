export default {
    props: ['documents'],
    template: `
                <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                    <div v-for="d in documents" :key="d.id" class="bg-white p-10 rounded-[3rem] shadow-xl border flex flex-col items-center hover:scale-105 transition-transform">
                        <span class="text-6xl mb-4">📄</span>
                        <p class="font-black text-slate-900 text-sm uppercase text-center tracking-tight">{{d.title}}</p>
                    </div>
                </div>
    `
}
