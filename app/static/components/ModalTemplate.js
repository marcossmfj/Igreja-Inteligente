export default {
    props: ['show', 'templates', 'funcoes', 'getPosName'],
    emits: ['close', 'delete-template', 'save-template'],
    data() {
        return {
            newTemplate: { name: '', positions: [] },
            templateAdd: { position_id: '', quantity: 1 }
        }
    },
    methods: {
        addPositionToTemplate() {
            if(!this.templateAdd.position_id) return;
            this.newTemplate.positions.push({ ...this.templateAdd });
            this.templateAdd = { position_id: '', quantity: 1 };
        },
        onSave() {
            this.$emit('save-template', this.newTemplate);
            this.newTemplate = { name: '', positions: [] };
        }
    },
    template: `
        <div v-if="show" class="fixed inset-0 modal-blur flex justify-center items-center z-[100] p-6">
            <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-10">
                    <h3 class="text-4xl font-black uppercase italic text-indigo-600">Organogramas 📋</h3>
                    <button @click="$emit('close')" class="text-4xl">&times;</button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
                    <!-- LISTA -->
                    <div class="space-y-4">
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-3 ml-2 italic">Modelos Ativos</p>
                        <div v-for="t in templates" :key="t.id" class="bg-slate-50 p-6 rounded-[2rem] border-2 border-slate-100 flex justify-between items-center group hover:border-indigo-200 transition-all">
                            <div>
                                <p class="font-black text-slate-800 uppercase text-sm tracking-tight">{{t.name}}</p>
                                <p class="text-[10px] font-bold text-slate-400 uppercase mt-1">
                                    {{ t.positions.length }} Funções Definidas
                                </p>
                            </div>
                            <button @click="$emit('delete-template', t.id)" class="text-slate-300 hover:text-red-500 transition-colors font-black text-xl p-2">🗑️</button>
                        </div>
                        <div v-if="templates.length === 0" class="text-center py-10 border-2 border-dashed rounded-[2rem] text-slate-300 font-bold uppercase text-xs">
                            Nenhum organograma criado
                        </div>
                    </div>

                    <!-- NOVO -->
                    <div class="bg-indigo-50/50 p-8 rounded-[2.5rem] border-2 border-indigo-100">
                        <p class="text-[10px] font-black text-indigo-400 uppercase mb-6 ml-2 italic text-center">Criar Novo Organograma</p>
                        <div class="space-y-4">
                            <input v-model="newTemplate.name" type="text" placeholder="Nome (Ex: Culto Domingo)" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-white focus:border-indigo-500">
                            
                            <div class="bg-white p-6 rounded-3xl border-2 border-indigo-50">
                                <p class="text-[10px] font-black text-slate-400 uppercase mb-4">Adicionar Função</p>
                                <div class="flex gap-2">
                                    <select v-model="templateAdd.position_id" class="flex-1 border-2 p-3 rounded-xl font-bold text-xs bg-slate-50 outline-none">
                                        <option value="">Selecione...</option>
                                        <option v-for="p in funcoes" :value="p.id">{{p.name}}</option>
                                    </select>
                                    <input v-model.number="templateAdd.quantity" type="number" min="1" class="w-20 border-2 p-3 rounded-xl font-bold text-xs bg-slate-50 outline-none text-center">
                                    <button @click="addPositionToTemplate" class="bg-indigo-600 text-white px-4 rounded-xl font-black text-sm">+</button>
                                </div>
                            </div>

                            <div class="space-y-2">
                                <div v-for="(tp, idx) in newTemplate.positions" :key="idx" class="flex justify-between items-center bg-white px-4 py-3 rounded-2xl border text-xs font-bold">
                                    <span>{{ getPosName(tp.position_id) }}</span>
                                    <div class="flex items-center gap-4">
                                        <span class="bg-indigo-100 text-indigo-600 px-3 py-1 rounded-lg">x{{tp.quantity}}</span>
                                        <button @click="newTemplate.positions.splice(idx, 1)" class="text-red-400">×</button>
                                    </div>
                                </div>
                            </div>

                            <button @click="onSave" class="w-full bg-indigo-600 text-white py-6 rounded-[2rem] font-black text-xl shadow-xl hover:scale-[1.02] transition-transform mt-4">Salvar Organograma ✅</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `
}
