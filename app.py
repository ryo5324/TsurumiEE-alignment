from flask import Flask, render_template, request
from collections import deque
from itertools import combinations

app = Flask(__name__)

# マッピング
letter_to_int = { 'A': 0, 'B': 1, 'C': 2 }
int_to_letter = ['A', 'B', 'C']

# 操作一覧
operations = [
    [1,0,0,1,0,0,0,0,0,0],  # ワープ2
    [1,1,1,1,1,0,0,0,0,1],  # ワープ3
    [0,1,1,1,1,1,0,0,0,0],  # ワープ4
    [0,1,0,0,1,1,1,1,1,0],  # ワープ5
    [1,1,1,0,1,1,1,1,1,0],  # ワープ6
    [1,0,0,0,0,0,0,0,0,1],  # ワープ7
    [0,0,0,0,0,0,0,0,0,1],  # ワープ8
    [1,1,0,0,0,0,0,0,0,1],  # 移動編モシリ炎アビス+モシリ雷アビス
    [1,0,0,0,0,0,0,1,0,1],  # 移動編アウタケ東
    [0,0,0,0,1,0,1,0,0,0],  # 移動編オイナ機兵＋シリコロ暴徒
]

# 移動編が必要か判定
def is_migration_needed(state, goal, idx1, idx2):
    if goal[idx1] is None or goal[idx2] is None:
        return False
    diff1 = (goal[idx1] - state[idx1]) % 3
    diff2 = (goal[idx2] - state[idx2]) % 3
    return diff1 != diff2

# 操作適用
def apply_ops_day(state, ops_used):
    added = [0] * 10
    for op in ops_used:
        for i in range(10):
            if operations[op][i]:
                added[i] = 1
    next_state = tuple((state[i] + added[i]) % 3 for i in range(10))
    return next_state

# ゴール判定
def is_goal(state, goal):
    for i in range(10):
        if goal[i] is None:
            continue
        if state[i] != goal[i]:
            return False
    return True

# BFS本体
def bfs(initial, goal):
    queue = deque()
    visited = set()

    queue.append((initial, []))
    visited.add(initial)

    need_moshiri = is_migration_needed(initial, goal, 1, 4)
    need_autake = is_migration_needed(initial, goal, 7, 8)
    need_shirikoro = is_migration_needed(initial, goal, 6, 8)

    active_ops = list(range(7))
    if need_moshiri:
        active_ops.append(7)
    if need_autake:
        active_ops.append(8)
    if need_shirikoro:
        active_ops.append(9)

    possible_ops = []
    for r in range(1, len(active_ops) + 1):
        possible_ops.extend(combinations(active_ops, r))

    while queue:
        current_state, history = queue.popleft()

        if is_goal(current_state, goal):
            return history

        for ops_used in possible_ops:
            next_state = apply_ops_day(current_state, ops_used)
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, history + [tuple(op + 1 for op in ops_used)]))

    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        initial = request.form.get('initial')
        goal_mode = request.form.get('goal_mode')
        goal_input = request.form.get('goal')

        # デフォルトゴール設定
        default_goal = ['C', 'B', 'C', 'C', 'C', 'B', '*', 'C', 'C', 'B']

        # 理想配置の決定
        if goal_mode == 'default':
            goal_letters = default_goal
        else:
            goal_letters = list(goal_input)

        # 入力チェック
        if not initial or len(initial) != 10 or any(ch not in 'ABC*' for ch in initial):
            return "エラー: 初期配置はA,B,C,*の10文字で入力してください。"
        if goal_mode == 'manual' and (not goal_input or len(goal_input) != 10 or any(ch not in 'ABC*' for ch in goal_input)):
            return "エラー: 理想配置はA,B,C,*の10文字で入力してください。"

        # 初期状態とゴール状態を数値化
        initial_state = tuple(letter_to_int.get(ch, 0) for ch in initial)
        goal_state = [letter_to_int.get(ch, None) if ch != '*' else None for ch in goal_letters]

        # パズルを解く
        solution = bfs(initial_state, goal_state)

        if solution:
            # ここで解を表示用に加工
            solution.reverse()  # 出力順を逆にする
            result = (
f"<h1>最短解</h1>"
f"<p><b>初期配置:</b> {initial}</p>"
f"<p><b>理想配置:</b> {''.join(goal_letters)}</p>"
f"<p>日数: {len(solution)} 日<br>(モシリ->移動編モシリ炎アビス+モシリ雷アビス, アウタケ->移動編アウタケ東, シリコロ->移動編オイナ機兵+シリコロ暴徒)</p><ul>"
)
            for day, ops in enumerate(solution, 1):
                ops_str = []
                for op in ops:
                    if op == 8:
                        ops_str.append("モシリ")
                    elif op == 9:
                        ops_str.append("アウタケ")
                    elif op == 10:
                        ops_str.append("シリコロ")
                    else:
                        ops_str.append(f"ワープ{op+1}")
                result += f"<li>Day {day}: {', '.join(ops_str)} を実行</li>"
            result += "</ul>"
            return result
        else:
            return "<h1>解が見つかりませんでした。</h1>"

    return render_template('form.html')


if __name__ == '__main__':
    app.run(debug=True)



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ... ここで処理 ...
        pass

    return render_template('form.html', link="https://youtu.be/2xqllaCTP5c")

