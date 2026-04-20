export default {
    props: ['show'],
    emits: ['close', 'upload'],
    data() {
        return {
            title: '',
            file: null,
            loading: false
        }
    },
    methods: {
        handleFileChange(e) {
            this.file = e.target.files[0];
        },
        async submit() {
            if (!this.title || !this.file) return alert("Preencha o título e selecione o arquivo!");
            this.loading = true;
            
            const formData = new FormData();
            formData.append('title', this.title);
            formData.append('file', this.file);

            this.$emit('upload', formData);
            
            // Reset local
            this.title = '';
            this.file = null;
            this.loading = false;
        }
    },
    template: `
    <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4 modal-blur">
        <div class="bg-white w-full max-w-lg rounded-[3rem] shadow-2xl overflow-hidden border border-slate-100 p-10">
            <div class="flex justify-between items-center mb-10">
                <h3 class="text-3xl font-black italic uppercase tracking-tighter text-indigo-600">Novo Arquivo</h3>
                <button @click="$emit('close')" class="text-slate-300 hover:text-slate-500 transition-colors text-2xl font-black">✕</button>
            </div>

            <div class="space-y-6">
                <div>
                    <label class="text-[10px] font-black text-slate-400 uppercase ml-2 mb-1 block tracking-widest">Nome do Documento</label>
                    <input v-model="title" type="text" placeholder="Ex: Estatuto da Igreja, Ata de Reunião..." 
                           class="w-full bg-slate-50 border-2 border-slate-100 p-5 rounded-2xl outline-none focus:border-indigo-500 font-bold transition-all">
                </div>

                <div>
                    <label class="text-[10px] font-black text-slate-400 uppercase ml-2 mb-1 block tracking-widest">Arquivo (PDF ou Imagem)</label>
                    <div class="relative group">
                        <input type="file" @change="handleFileChange" accept=".pdf,image/*"
                               class="w-full bg-slate-50 border-2 border-dashed border-slate-200 p-12 rounded-2xl outline-none group-hover:border-indigo-300 transition-all font-bold text-center file:hidden">
                        <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-slate-400 group-hover:text-indigo-500 transition-colors">
                            <span class="text-4xl mb-2">📁</span>
                            <span class="text-[10px] font-black uppercase tracking-widest">
                                {{ file ? file.name : 'Clique para selecionar arquivo' }}
                            </span>
                        </div>
                    </div>
                </div>

                <button @click="submit" :disabled="loading"
                        class="w-full bg-indigo-600 text-white py-6 rounded-[2rem] font-black text-xl shadow-xl shadow-indigo-100 hover:bg-indigo-700 transition-all flex items-center justify-center gap-4">
                    <span v-if="loading">Enviando Arquivo...</span>
                    <span v-else>Guardar na Nuvem ☁️</span>
                </button>
            </div>
        </div>
    </div>
    `
}
