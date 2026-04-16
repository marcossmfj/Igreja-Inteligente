export default {
    props: ['show', 'substitutes'],
    emits: ['close', 'apply'],
    template: `
        <div v-if="show" class="fixed inset-0 modal-blur flex justify-center items-center z-[100] p-6">
            <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-lg text-center">
                <h3 class="text-3xl font-black mb-8 uppercase italic text-indigo-600">Sugestões de IA 🤖</h3>
                <div class="space-y-3">
                    <div v-for="sub in substitutes" :key="sub.id" class="bg-slate-50 p-6 rounded-3xl flex justify-between items-center border-2 border-slate-100">
                        <span class="font-black text-slate-700">{{sub.name}}</span>
                        <button @click="$emit('apply', sub)" class="bg-indigo-600 text-white px-6 py-3 rounded-2xl font-black text-xs">Trocar</button>
                    </div>
                    <button @click="$emit('close')" class="w-full text-slate-400 font-black text-xs uppercase mt-6">Fechar</button>
                </div>
            </div>
        </div>
    `
}
