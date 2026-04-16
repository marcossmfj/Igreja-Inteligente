export default {
    props: ['show', 'templates'],
    emits: ['close', 'run-auto-batch'],
    data() {
        return {
            autoBatchData: { event_name: '', start_date: '', end_date: '', days_of_week: [], template_id: '' }
        }
    },
    methods: {
        toggleDay(day) {
            const idx = this.autoBatchData.days_of_week.indexOf(day);
            if (idx > -1) this.autoBatchData.days_of_week.splice(idx, 1);
            else this.autoBatchData.days_of_week.push(day);
        }
    },
    template: `
        <div v-if="show" class="fixed inset-0 modal-blur flex justify-center items-center z-[100] p-6">
            <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-2xl">
                <div class="flex justify-between items-center mb-10">
                    <h3 class="text-4xl font-black uppercase italic text-indigo-600">Geração por IA 🚀</h3>
                    <button @click="$emit('close')" class="text-4xl">&times;</button>
                </div>
                <div class="space-y-6">
                    <div>
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-3 ml-2">Nome do Evento</p>
                        <input v-model="autoBatchData.event_name" type="text" placeholder="Ex: Culto de Celebração" class="w-full border-2 p-5 rounded-3xl font-black outline-none focus:border-indigo-500 bg-slate-50">
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <p class="text-[10px] font-black text-slate-400 uppercase mb-3 ml-2">Início</p>
                            <input v-model="autoBatchData.start_date" type="date" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                        </div>
                        <div>
                            <p class="text-[10px] font-black text-slate-400 uppercase mb-3 ml-2">Fim (Planejamento)</p>
                            <input v-model="autoBatchData.end_date" type="date" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                        </div>
                    </div>

                    <div>
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-3 ml-2 text-center">Dias da Semana</p>
                        <div class="grid grid-cols-7 gap-2">
                            <button v-for="(day, idx) in ['D','S','T','Q','Q','S','S']" :key="idx" 
                                    @click="toggleDay(idx)" 
                                    :class="['day-btn', autoBatchData.days_of_week.includes(idx) ? 'active' : '']">
                                {{day}}
                            </button>
                        </div>
                    </div>

                    <div>
                        <p class="text-[10px] font-black text-slate-400 uppercase mb-3 ml-2">Template (Organograma)</p>
                        <select v-model="autoBatchData.template_id" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                            <option value="">Selecione a Estrutura...</option>
                            <option v-for="t in templates" :value="t.id">{{t.name}}</option>
                        </select>
                    </div>

                    <button @click="$emit('run-auto-batch', autoBatchData)" class="w-full bg-indigo-600 text-white py-6 rounded-[2.5rem] font-black text-xl shadow-xl mt-6 hover:scale-[1.02] transition-transform">IA: Gerar Planejamento Completo 🤖</button>
                </div>
            </div>
        </div>
    `
}
