export default {
    props: ['show', 'positions', 'getQualifiedMembers'],
    emits: ['close', 'run-manual-add'],
    data() {
        return {
            newSchedule: { event_name: '', event_date: '', position_id: '', member_id: '' }
        }
    },
    template: `
        <div v-show="show" class="fixed inset-0 modal-blur flex justify-center items-center z-[100] p-6 text-center">
            <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-lg">
                <h3 class="text-3xl font-black mb-8 uppercase italic text-indigo-600">Escala Única (Manual)</h3>
                <div class="space-y-5 text-left">
                    <input v-model="newSchedule.event_name" type="text" placeholder="Nome do Evento" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                    <input v-model="newSchedule.event_date" type="datetime-local" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                    <select v-model="newSchedule.position_id" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                        <option value="">Selecione a Função...</option>
                        <option v-for="p in positions" :value="p.id">{{p.name}}</option>
                    </select>
                    <select v-model="newSchedule.member_id" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                        <option value="">Selecione o Voluntário...</option>
                        <option v-for="m in getQualifiedMembers(newSchedule.position_id)" :value="m.id">{{m.name}}</option>
                    </select>
                    <button @click="$emit('run-manual-add', newSchedule)" class="w-full bg-emerald-500 text-white py-6 rounded-[2rem] font-black text-xl mt-4 shadow-xl">Salvar Escala ✅</button>
                    <button @click="$emit('close')" class="w-full text-slate-400 font-black text-xs uppercase mt-4 block">Cancelar</button>
                </div>
            </div>
        </div>
    `
}
