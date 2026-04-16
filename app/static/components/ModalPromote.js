export default {
    props: ['show', 'targetPromotion', 'cargos', 'funcoes'],
    emits: ['close', 'confirm'],
    data() {
        return {
            promotionData: { cargo_id: '', selectedFuncoes: [] }
        }
    },
    template: `
        <div v-if="show" class="fixed inset-0 modal-blur flex justify-center items-center z-[100] p-6">
            <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-lg text-center overflow-y-auto max-h-[90vh]">
                <h3 class="text-3xl font-black mb-4 uppercase italic text-indigo-600">Promover Membro</h3>
                <p class="mb-6 font-bold text-slate-400">Promovendo: {{targetPromotion?.name}}</p>
                
                <div class="space-y-4 text-left">
                    <div>
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2">Cargo Ministerial</p>
                        <select v-model="promotionData.cargo_id" class="w-full border-2 p-4 rounded-2xl font-bold outline-none bg-slate-50">
                            <option value="">Selecione um Cargo...</option>
                            <option v-for="c in cargos" :value="c.id">{{c.name}}</option>
                        </select>
                    </div>

                    <div>
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2">Funções na Escala</p>
                        <div class="flex flex-wrap gap-2 p-2 border-2 rounded-2xl bg-slate-50 max-h-40 overflow-y-auto">
                            <label v-for="f in funcoes" :key="f.id" class="flex items-center gap-2 bg-white px-3 py-1 rounded-lg border text-[10px] font-bold cursor-pointer">
                                <input type="checkbox" :value="f.id" v-model="promotionData.selectedFuncoes">
                                {{f.name}}
                            </label>
                        </div>
                    </div>

                    <button @click="$emit('confirm', promotionData)" class="w-full bg-indigo-600 text-white py-6 rounded-[2rem] font-black text-xl shadow-xl hover:bg-indigo-700 transition-all">Confirmar Promoção 🚀</button>
                    <button @click="$emit('close')" class="w-full text-slate-400 font-black text-xs uppercase mt-2">Cancelar</button>
                </div>
            </div>
        </div>
    `
}
