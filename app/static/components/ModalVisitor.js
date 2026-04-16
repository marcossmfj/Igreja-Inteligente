export default {
    props: ['show'],
    emits: ['close', 'save'],
    data() {
        return {
            newVisitor: { name: '', whatsapp: '', email: '', status: 'Visitante' }
        }
    },
    template: `
        <div v-if="show" class="fixed inset-0 modal-blur flex justify-center items-center z-[100] p-6">
            <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-lg text-center">
                <h3 class="text-3xl font-black mb-8 uppercase italic text-emerald-600">Novo Visitante</h3>
                <div class="space-y-4 text-left">
                    <input v-model="newVisitor.name" type="text" placeholder="Nome do Visitante" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                    <input v-model="newVisitor.whatsapp" type="text" placeholder="WhatsApp" class="w-full border-2 p-5 rounded-3xl font-black outline-none bg-slate-50">
                    <button @click="$emit('save', newVisitor)" class="w-full bg-emerald-500 text-white py-6 rounded-[2rem] font-black text-xl shadow-xl">Registrar Entrada</button>
                    <button @click="$emit('close')" class="w-full text-slate-400 font-black text-xs uppercase mt-2">Cancelar</button>
                </div>
            </div>
        </div>
    `
}
