export default {
    props: ['show', 'positions', 'getQualifiedMembers', 'initialData'],
    emits: ['close', 'save'],
    data() {
        return {
            quickAddData: { event_name: '', event_date: '', position_id: '', member_id: '' }
        }
    },
    watch: {
        initialData: {
            handler(val) { if(val) this.quickAddData = { ...this.quickAddData, ...val }; },
            immediate: true
        }
    },
    template: `
        <div v-if="show" class="fixed inset-0 modal-blur flex justify-center items-center z-[100] p-6">
            <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-lg text-center">
                <h3 class="text-3xl font-black mb-8 uppercase italic text-indigo-600">Incluir Voluntário</h3>
                <div class="space-y-4 text-left">
                    <select v-model="quickAddData.position_id" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                        <option value="">Selecione a Função...</option>
                        <option v-for="p in positions" :value="p.id">{{p.name}}</option>
                    </select>
                    <select v-model="quickAddData.member_id" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                        <option value="">Selecione o Membro...</option>
                        <option v-for="m in getQualifiedMembers(quickAddData.position_id)" :value="m.id">{{m.name}}</option>
                    </select>
                    <button @click="$emit('save', quickAddData)" class="w-full bg-indigo-600 text-white py-6 rounded-[2rem] font-black text-xl shadow-xl">Adicionar à Escala</button>
                    <button @click="$emit('close')" class="w-full text-slate-400 font-black text-xs uppercase mt-2">Cancelar</button>
                </div>
            </div>
        </div>
    `
}
