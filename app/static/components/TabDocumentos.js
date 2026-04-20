export default {
    props: ['documents'],
    emits: ['show-modal-upload', 'delete-doc'],
    template: `
                <div class="space-y-6">
                    <div class="flex justify-between items-center mb-10">
                        <div>
                            <h2 class="text-5xl font-black tracking-tight text-slate-900">Documentos & Arquivos</h2>
                            <p class="text-slate-500 font-bold mt-2">Repositório central de certificados, regimentos e avisos.</p>
                        </div>
                        <button @click="$emit('show-modal-upload')" class="bg-indigo-600 text-white px-8 py-4 rounded-2xl font-black shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all">
                            Novo Documento +
                        </button>
                    </div>

                    <div v-if="documents.length === 0" class="bg-white p-20 rounded-[3rem] shadow-xl border border-dashed border-slate-200 flex flex-col items-center justify-center text-center">
                        <span class="text-7xl mb-6">📁</span>
                        <h3 class="text-xl font-black text-slate-400 uppercase tracking-widest">Nenhum documento arquivado</h3>
                        <p class="text-slate-300 font-bold mt-2">Comece subindo PDFs ou imagens importantes para a igreja.</p>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-8">
                        <div v-for="d in documents" :key="d.id" class="group bg-white p-8 rounded-[3rem] shadow-xl border border-slate-100 flex flex-col items-center hover:scale-105 transition-all relative overflow-hidden">
                            <!-- Ícone Dinâmico -->
                            <div class="text-6xl mb-4 group-hover:rotate-12 transition-transform">
                                {{ d.file_type.includes('pdf') ? '📕' : '🖼️' }}
                            </div>
                            
                            <p class="font-black text-slate-900 text-sm uppercase text-center tracking-tight leading-tight mb-6 line-clamp-2 min-h-[40px]">
                                {{d.title}}
                            </p>

                            <div class="flex gap-2 w-full">
                                <a :href="'/' + d.file_path" target="_blank" class="flex-1 bg-slate-900 text-white text-[10px] font-black py-3 rounded-2xl text-center uppercase tracking-wider hover:bg-slate-800 transition-colors">
                                    Abrir 👁️
                                </a>
                                <button @click="$emit('delete-doc', d.id)" class="bg-rose-50 text-rose-500 px-4 py-3 rounded-2xl hover:bg-rose-100 transition-colors">
                                    🗑️
                                </button>
                            </div>

                            <!-- Badge de Tipo -->
                            <span class="absolute top-4 right-6 text-[8px] font-black text-slate-300 uppercase tracking-widest">
                                {{ d.file_type.split('/')[1] }}
                            </span>
                        </div>
                    </div>
                </div>
    `
}
